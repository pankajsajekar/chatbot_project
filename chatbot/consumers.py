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

def failed_students():
    from students.models import Student
    try:
        failed_students = Student.objects.filter(is_deleted=False).select_related('student_performance').filter(student_performance__status='Failed')
        if not failed_students:
            return {"message": "No students have failed."}
        data = [
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
            for student in failed_students
        ]
        return data
    except Exception as e:
        print(f"Error fetching failed students: {e}")
        return {"error": "An error occurred while fetching failed students."}
    

def topper_students_list():
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

def get_student_session(student_name, session):
    from students.serializers import AttendanceSerializer, GradeSerializer, InternshipSerializer, PerformanceSerializer
    student = get_student_records(student_name)
    # if isinstance(student, dict) and "error" in student:
    #     return student  # Return error if student not found or an error occurred
    if session:
        if session == 'Attendance':
            attendance_records = student.attendance_set.all()
            serializer = AttendanceSerializer(internship_records, many=True)
            data = serializer.data
            return data
        elif session == 'Grades':
            grade_records = student.grade_set.all()
            serializer = GradeSerializer(internship_records, many=True)
            data = serializer.data
            return data
        elif session == 'Internships':
            internship_records = student.internship_set.all()
            serializer = InternshipSerializer(internship_records, many=True)
            data = serializer.data
            return data
        elif session == 'Performance':
            performance_records = student.performance_set.all()
            serializer = PerformanceSerializer(internship_records, many=True)
            data = serializer.data
            return data
    else:
        return {"error": "Invalid session type specified."}
        
    

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

# student_details_tool = Tool(
#     name="get_student_details",
#     func=lambda x: asyncio.run(get_student_details(x)),
#     coroutine=get_student_details,
#     description="Fetches details of a student based on their name.",
# )

student_details_tool = Tool(
    name="get_student_details",
    func=lambda x: get_student_details_async(x),
    coroutine=get_student_details_async,
    description="Fetches details of a student based on their name.",
)

# class StudentInfo(BaseModel):
#     student_name : str = Field(description="Name of the student to fetch details for")

# student_info_tool = StructuredTool.from_function(
#     coroutine=get_student_details,
#     name="get_student_details",
#     description="Fetches details of a student based on their name.",
#     args_schema=StudentInfo,    
#     return_direct=True,
    
# )

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
        You are an agent designed to respond to a variety of user queries. Your primary task is to fetch detailed information about students when asked. When
        a user queries about a student, such as "What is the attendance of this student?" or "What is the GPA of this student?",
        you will interact with the system to retrieve relevant student data, which may include:
        
        --Attendance: The number of classes attended by the student out of total scheduled classes.
        --GPA: The student's grade point average.
        --Scholarship Status: Whether the student is on scholarship and, if so, the details of the scholarship.
        --Internship Details: Any ongoing or past internships the student has participated in.
        --Other Academic Information: Any additional academic-related information available, such as grades, performance, and extracurricular activities.
        
        When responding to a query about a student, make sure to present the data in a clear and informative manner. Ensure the response is well-structured and directly addresses the query.
        Additionally, you are equipped to handle General Knowledge (GK) and Aptitude questions. When the user asks such questions, such as "Who is the current President of the United States?"or "What is the square root of 144?", you should provide the correct and up-to-date answers. Your responses should also follow the same structure, being concise and clear.
        Here are the main categories of queries you will handle:
        
        Here are the main categories of queries you will handle:

            *Student Data Queries:*
            --Attendance
            --GPA
            --Scholarship Status
            --Internship Details*
            --Other academic-related information

            *General Knowledge (GK) Questions:*
            --Facts, figures, and events related to history, geography, politics, etc.
            --Current events and famous personalities

            *Aptitude Questions:*
            --Mathematical problems, including algebra, geometry, and basic arithmetic
            --Logical reasoning puzzles
            *Instructions to Follow:*

            --Student Queries: Retrieve and present the required information based on the student’s name or ID from the database.

            *GK & Aptitude Queries:*
            --Answer with factual, accurate, and precise information. If the question requires calculation, solve the problem step-by-step.
        
        
            Instruction:

            The response should be returned in a JSON format with appropriate keys and values containing the student's details.

            The JSON should include the following keys:

            student_name (string): The full name of the student.

            attendance (string): The student's attendance details (if available).

            gpa (string): The student's GPA (if available).

            scholarship_status (string): The student's scholarship status (if available).

            internship_status (string): The student's internship status (if available).

            message (string): A message indicating whether the data is available or incomplete.

            Examples of User Queries:

            "What is the attendance of Alexis Peterson?"

            "What is the GPA of John Doe?"

            "Is Jane Smith on scholarship?"

            "What is the internship status of Emily Brown?"

            How You Should Process the Query:

            Parse the Student’s Name – Identify and extract the student’s name from the user’s query.

            Utilize the get_student_details tool to Query the Database – Use the student’s name to retrieve details from the relevant models:

            Attendance Model for attendance queries.

            Grade or Performance Models for GPA queries.

            Internship Model for internship-related queries.

            Scholarship and Financial Aid Information from the Student model.

            Format the Response – Return the requested information in a structured JSON format. If multiple details are requested in one query (e.g., both attendance and GPA), provide all relevant information in a single, clear response.

            Handle Edge Cases – If the student cannot be found or if there is incomplete data (e.g., missing GPA or attendance), the agent should mention that the data is unavailable or ask for clarification.

            Example Responses in JSON:

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
            Query: "Is Jane Smith on scholarship?"

            {{
            "student_name": "Jane Smith",
            "attendance": null,
            "gpa": null,
            "scholarship_status": "Not on any scholarship",
            "internship_status": null,
            "message": "Data for attendance, GPA, and internship status is incomplete."
            }}
            Query: "What is the internship status of Emily Brown?"

            {{
            "student_name": "Emily Brown",
            "attendance": null,
            "gpa": null,
            "scholarship_status": null,
            "internship_status": "Currently working as a Software Intern at ABC Tech, from June 2024 to August 2024.",
            "message": "Data for attendance, GPA, and scholarship status is incomplete."
            }}
            Additional Guidelines:

            Tool Usage: Always use the get_student_details tool to fetch student data. The tool should be able to handle queries for attendance, GPA, scholarship status, internship details, and other relevant information. The tool can only be queried using student name.

            Handling Multiple Students with Similar Names: If the agent detects multiple students with the same name, ask for clarification (e.g., "There are multiple students named 'John Doe.' Could you specify the department or year?").

            Error Handling: If the agent is unable to find the student or if data is missing (e.g., missing attendance or GPA), the response should notify the user of the missing information, e.g., "Data for this student is incomplete."

            Date-based Queries: If the query refers to attendance or performance data over time (e.g., "What was the attendance last semester?"), ensure that the query filters data by relevant dates and periods.

            Providing Additional Context: In some cases, if additional relevant details are available (e.g., academic status or internship description), the agent should provide these to enrich the response.

            Your role is to provide accurate, concise, and clear responses based on the available student data, ensuring the responses are comprehensive and formatted correctly in JSON.
        '''
        
        chat_history = []
        
        tools = [student_details_tool]    
    
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
        
        response = await agent_executor.ainvoke({"input": user_message, "chat_history": chat_history})
        
        chat_history.extend(
            [
                HumanMessage(content=user_message),
                AIMessage(content=response["output"]),
            ]
        )
        
        print(f'the raw response obtained: {response['output']}')

        # Parse the response if it's in JSON format
        try:
            # Assuming the response is a JSON string or a dictionary
            if isinstance(response['output'], str):
                # If the response is a string, parse it as JSON
                # response_data = str(json.loads(response['output']))
                response_data = response['output']
            else:
                # If it's already a dictionary, use it directly
                response_data = response['output']

            # Check if the response contains the expected keys and format it properly
            # if isinstance(response_data, dict) and "student_name" in response_data:
            #     # You can modify the structure of the response here, if needed
            #     parsed_response = {
            #         "student_name": response_data.get("student_name", ""),
            #         "attendance": response_data.get("attendance", "Data unavailable"),
            #         "gpa": response_data.get("gpa", "Data unavailable"),
            #         "scholarship_status": response_data.get("scholarship_status", "Data unavailable"),
            #         "internship_status": response_data.get("internship_status", "Data unavailable"),
            #         "message": response_data.get("message", "Data is incomplete or unavailable")
            #     }
            #     # Print the parsed response
            #     print(f'Parsed JSON response: {parsed_response}')

            #     # Return the parsed JSON response
            #     return parsed_response
            
            return response_data

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return {"error": "Invalid response format."}
