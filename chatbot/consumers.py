import json
import openai
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain.tools import Tool, StructuredTool
from langchain_core.messages import AIMessage, HumanMessage
from typing import Annotated
from pydantic import BaseModel, Field
from asgiref.sync import sync_to_async
import asyncio
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

MEMORY_KEY = "chat_history"

# Set up OpenAI API key
openai.api_key = settings.OPENAI_API_KEY

llm = ChatOpenAI(model="gpt-4.1", temperature=0.3, api_key=settings.OPENAI_API_KEY)

def get_list_students(self):
    from students.models import Student
    from students.serializers import StudentSerializer
    try:
        students = Student.objects.filter(is_deleted=False)
        if not students:
            return {"message": "No students found."}
        serializers = StudentSerializer(students, many=True)
        return serializers.data
    except Exception as e:
        print(f"Error fetching students: {e}")
        return {"error": "An error occurred while fetching students."}

get_students_list_async = sync_to_async(get_list_students)

student_records_tool = Tool(
    name="get_students_list",
    func=lambda x: get_students_list_async(x),
    coroutine=get_students_list_async,
    description="Fetches a list of all students who are not marked as deleted."
)

def get_student_records(student_name):
    from students.models import Student
    try:
        student = Student.objects.filter(name__icontains=student_name).first()
        if not student:
            return {"error": "Student not found."}
        return student
    except Exception as e:
        print(f"Error fetching student details: {e}")
        return {"error": "An error occurred while fetching student details."}

get_student_records_async = sync_to_async(get_student_records)

student_records_tool = Tool(
    name="get_student_records",
    func=lambda x: get_student_records_async(x),
    coroutine=get_student_records_async,
    description="Fetches a student's record based on their name."
)

def count_total_records(items: str):
    """
    Count the total number of records in the specified model.
    :param items: The name of the model to count records for.
    """
    from students.models import Student, Attendance, Grade, Course, Internship, Performance
    try:
        if items == "students":
            total_count = Student.objects.count()
        elif items == "courses":
            total_count = Course.objects.count()
        elif items == "internships":
            total_count = Internship.objects.count()
        elif items == "performances":
            total_count = Performance.objects.count()
        elif items == "attendance":
            total_count = Attendance.objects.count()
        elif items == "grades":
            total_count = Grade.objects.count()
        else:
            return Student.objects.count()
        return total_count
    except Exception as e:
        print(f"Error counting students: {e}")
        return {"error": "An error occurred while counting students."}

count_total_records_async = sync_to_async(count_total_records)

count_records_tool = Tool(
    name="count_total_records",
    func=lambda x: count_total_records_async(x),
    coroutine=count_total_records_async,
    description="Counts total records for a given model (students, courses, internships, etc.)."
)

def failed_students(self):
    from students.models import Student
    try:
        # Use prefetch_related for reverse relationships
        failed_students = Student.objects.prefetch_related('student_performance__course').filter(
            is_deleted=False, student_performance__status='Failed'
        )
        if not failed_students:
            return {"message": "No students have failed."}
        
        data = []
        # Iterate and collect relevant information
        for student in failed_students:
            for performance in student.student_performance.all():  # Access related performances
                data.append({
                    "name": student.name,
                    "student_id": student.student_id,
                    "department": student.department,
                    "email": student.email,
                    "phone_number": student.phone_number,
                    "gpa": student.gpa,
                    "status": student.status,
                    "enrollment_year": student.enrollment_year,
                    "graduation_year": student.graduation_year,
                    "course": performance.course.name,  # Include course name
                    "performance_status": performance.status,
                })
        
        return data
    except Exception as e:
        print(f"Error fetching failed students: {e}")
        return {"error": "An error occurred while fetching failed students."}

failed_students_async = sync_to_async(failed_students)

failed_students_tool = Tool(
    name="failed_students",
    func=lambda: failed_students_async(),
    coroutine=failed_students_async,
    description="Fetches a list of failed students."
)    

def topper_students_list(self):
    from students.models import Student
    try:
        top_students = Student.objects.filter(is_deleted=False).order_by('-gpa')[:10]
        if not top_students:
            return {"message": "No students found."}
        return [
            {
                "name": student.name,
                "student_id": student.student_id,
                "department": student.department,
                "email": student.email,
                "phone_number": student.phone_number,
                "gpa": student.gpa,
                "status": student.status,
                "enrollment_year": student.enrollment_year,
                "graduation_year": student.graduation_year,
            }
            for student in top_students
        ]
    except Exception as e:
        print(f"Error fetching top students: {e}")
        return {"error": "An error occurred while fetching top students."}

topper_students_list_async = sync_to_async(topper_students_list)

topper_students_tool = Tool(
    name="topper_students_list",
    func=lambda: topper_students_list_async(),
    coroutine=topper_students_list_async,
    description="Fetches a list of the top 10 students based on GPA."
)

class StudentSessionInput(BaseModel):
    student_name: str = Field(description="Name of the student")
    session: str = Field(description="Session type (Attendance, Grades, Internships, Performance)")

def get_student_session(student_name, session):
    from students.serializers import AttendanceSerializer, GradeSerializer, InternshipSerializer, PerformanceSerializer
    student = get_student_records(student_name)
    # if isinstance(student, dict) and "error" in student:
    #     return student  # Return error if student not found or an error occurred
    if session:
        if session == 'Attendance':
            attendance_records = student.student_attendance.all()
            serializer = AttendanceSerializer(attendance_records, many=True)
            data = serializer.data
            return data
        elif session == 'Grades':
            grade_records = student.student_grades.all()
            serializer = GradeSerializer(grade_records, many=True)
            data = serializer.data
            return data
        elif session == 'Internships':
            internship_records = student.student_internships.all()
            serializer = InternshipSerializer(internship_records, many=True)
            data = serializer.data
            return data
        elif session == 'Performance':
            performance_records = student.student_performance.all()
            serializer = PerformanceSerializer(performance_records, many=True)
            data = serializer.data
            return data
    else:
        return {"error": "Invalid session type specified."}
        
get_student_session_async = sync_to_async(get_student_session)

# student_session_tool = Tool(
#     name="get_student_session",
#     func=lambda x, y: get_student_session_async(x, y),
#     coroutine=get_student_session_async,
#     description="Fetches a student's session data (Attendance, Grades, Internships, Performance) based on session type."
# )

student_session_tool = Tool(
    name="get_student_session",
    func=lambda x: get_student_session_async(**json.loads(x)),
    coroutine=lambda x: get_student_session_async(**json.loads(x)),
    description="Fetches a student's session data (Attendance, Grades, Internships, Performance) based on session type. Input should be JSON format like: {\"student_name\": \"John Doe\", \"session\": \"Attendance\"}"
)

def get_student_details_sync(student_name):
    from students.models import Student, Attendance, Grade, Course, Internship, Performance
    from students.serializers import StudentSerializer
    try:
        student = get_student_records(student_name)
        serializer = StudentSerializer(student)
        student_details = serializer.data
        return student_details
    
    except Exception as e:
        print(f"Error fetching student details: {e}")
        return {"error": "An error occurred while fetching student details."}

get_student_details_async = sync_to_async(get_student_details_sync)

student_details_tool = Tool(
    name="get_student_details",
    func=lambda x: get_student_details_async(x),
    coroutine=get_student_details_async,
    description="Fetches details of a student based on their name.",
)



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'chat_room'
        self.room_group_name = f'chat_{self.room_name}'

        # Join WebSocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send the message to OpenAI and get the response
        ai_response = await self.get_ai_response(message)

        # Send the AI response to WebSocket
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': ai_response
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    # Function to interact with OpenAI API (correct method)
    async def get_ai_response(self, user_message):
        
        base_prompt = '''
        You are an agent designed to respond to a variety of user queries. Your primary task is to fetch detailed information about students, courses, and academic records when asked. When a user queries about a student or academic data, such as "What is the attendance of this student?" or "What is the GPA of this student?", you will interact with the system to retrieve relevant data, which may include:

        *Student Data Queries:*
        --Attendance: The number of classes attended by the student out of total scheduled classes.
        --GPA: The student's grade point average.
        --Scholarship Status: Whether the student is on scholarship and, if so, the details of the scholarship.
        --Internship Details: Any ongoing or past internships the student has participated in.
        --Other Academic Information: Any additional academic-related information available, such as grades, performance, and extracurricular activities.

        *General Knowledge (GK) Questions:*
        --Facts, figures, and events related to history, geography, politics, etc.
        --Current events and famous personalities.

        *Aptitude Questions:*
        --Mathematical problems, including algebra, geometry, and basic arithmetic.
        --Logical reasoning puzzles.

        You are also capable of handling queries regarding the overall records and counts of various entities in the system:

        *General Queries:*
        - Total Students: The total number of students in the system.
        - Total Courses: The total number of courses available.
        - Total Grades: The number of grades recorded in the system.
        - Total Attendance Records: The number of attendance records available.
        - Total Performance Records: The number of performance records available.
        - Active Internships: The number of ongoing internships.
        - List of Students: Fetch the list of all students who are not marked as deleted.

        How You Should Process the Query:
        1. **Student Queries**: Retrieve and present the required information based on the student’s name or ID from the database.
            - Use the **get_student_details_tool** for full student details.
            - Use the **student_session_tool** to fetch session data like attendance, grades, internships, and performance.
            - Use the **failed_students_tool** and **topper_students_tool** for specific data on students who have failed or the top students by GPA.
        2. **General Queries**: For queries related to total numbers (like total students or courses), fetch the appropriate count from the system:
            - **count_records_tool** for retrieving the total number of records (e.g., students, courses, grades, etc.).
            - Use the **get_students_list** tool to fetch the list of all students.

        3. **Format the Response**: Return the requested information in a structured text format. If multiple details are requested in one query (e.g., both attendance and GPA), provide all relevant information in a single, clear response.

        4. **Handle Edge Cases**: If the student cannot be found or if data is missing (e.g., missing GPA or attendance), the agent should mention that the data is unavailable or ask for clarification.

        Examples of User Queries:

        1. "What is the attendance of Alexis Peterson?"
        2. "What is the GPA of John Doe?"
        3. "Is Jane Smith on scholarship?"
        4. "What is the internship status of Emily Brown?"
        5. "How many students are there in total?"
        6. "How many courses are available?"
        7. "How many active internships are there?"
        8. "What is the total number of performance records?"
        9. "Show me the grades for all students."
        10. "List all students in the system."


        First you need to fetch all the details and store them in a JSON format.
        Example Responses that you need to store in JSON: 

        Query: "What is the attendance of Alexis Peterson?"
        {{
            "student_name": "Alexis Peterson",
            "attendance": "80% attendance in the 'Mathematics' course this semester",
            "gpa": null,
            "scholarship_status": null,
            "internship_status": null,
            "message": "Data for GPA, scholarship status, and internship status is incomplete."
        }}

        Query: "What is the GPA of John Doe?"
        {{
            "student_name": "John Doe",
            "attendance": null,
            "gpa": "3.75 for the current semester",
            "scholarship_status": null,
            "internship_status": null,
            "message": "Data for attendance, scholarship status, and internship status is incomplete."
        }}

        Query: "How many students are there in total?"
        {{
            "total_students": 11
        }}

        Query: "List all students in the system."
        {{
            "students": [
            {"name": "John Doe", "student_id": "12345", "department": "Computer Science"},
            {"name": "Jane Smith", "student_id": "67890", "department": "Mathematics"},
            ...
            ]
        }}

        Once you have the JSON with you, convert it into a proper, precise, concise, readable, easy-to-understand formatted text string and return it.

        Additional Guidelines:
        - **Tool Usage**: Always use the appropriate tool to fetch student data (e.g., `get_student_details_tool`, `get_student_session_tool`, etc.). The tool should be able to handle queries for attendance, GPA, internship details, and other relevant information.
        - **Handling Multiple Students with Similar Names**: If the agent detects multiple students with the same name, ask for clarification (e.g., "There are multiple students named 'John Doe.' Could you specify the department or year?").
        - **Error Handling**: If the agent is unable to find the student or if data is missing (e.g., missing attendance or GPA), the response should notify the user of the missing information, e.g., "Data for this student is incomplete."
        - **Date-based Queries**: If the query refers to attendance or performance data over time (e.g., "What was the attendance last semester?"), ensure that the query filters data by relevant dates and periods.
        - **Providing Additional Context**: In some cases, if additional relevant details are available (e.g., academic status or internship description), the agent should provide these to enrich the response.
        - For using get_student_session_tool, first determine the session based on the user query context. There are only 4 session types: Attendance, Grades, Internships, Performance. Once you have the session variable, you can call the get_student_session_tool with the student name and session. For example, if the user asks for "What is the attendance of Pankaj?", you will set session = Attendance and call get_student_session_tool with first variable x = Pankaj, and second variable y = Attendance. The tool will return the attendance records of Pankaj.

        Your role is to provide accurate, concise, and clear responses based on the available student data, ensuring the responses are comprehensive and formatted correctly as text. Format the data in such a way that it should have bullet points or the data should be structured in the form of a table if required.
        '''
        
        chat_history = []
        
        tools = [student_details_tool, student_records_tool, count_records_tool, failed_students_tool, topper_students_tool, student_session_tool]    
    
        llm_with_tools = llm.bind_tools(tools)
        
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    base_prompt,
                ),
                MessagesPlaceholder(variable_name=MEMORY_KEY),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        
        agent = (
            {
                "input": lambda x: x["input"],
                "agent_scratchpad": lambda x: format_to_openai_tool_messages(
                    x["intermediate_steps"]
                ),
                "chat_history": lambda x: x["chat_history"]
            }
            | prompt
            | llm_with_tools
            | OpenAIToolsAgentOutputParser()
        )
        
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        try:
            response = await agent_executor.ainvoke({"input": user_message, "chat_history": chat_history})
            
            chat_history.extend(
                [
                    HumanMessage(content=user_message),
                    AIMessage(content=response["output"]),
                ]
            )
            
            # print(f'the raw response obtained: {response['output']}')

            # # Parse the response if it's in JSON format
            # try:
            #     # Assuming the response is a JSON string or a dictionary
            #     if isinstance(response['output'], str):
            #         # If the response is a string, parse it as JSON
            #         print(f'Parsing response: {response["output"]}')
            #         response_data = json.loads(response['output'])
            #         if 'answer' in response_data:
            #             response_data = response_data['answer']
            #         else:
            #             response_data = str(response_data)
            #         # response_data = response['output']            
                
            #     return response_data
            
            return response['output']

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {"error": "Invalid response format."}
        

