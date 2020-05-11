from locust import HttpLocust, TaskSet, TaskSequence, seq_task, between
from random import randrange
import json
import csv

#constants
email_password = []

#functions
with open('/locust-tasks/email_password_embibe.csv', 'r') as csvfile:
        email_password = list (csv.reader(csvfile, delimiter=','))

#Declarations
headers = {
    'Connection':'keep-alive',
    'Accept':'application/json, text/plain, */*',
    'Content-Type':'application/json;charset=UTF-8',
          }
     
#Payload Values       
body = {}

class MyTaskSequence(TaskSequence):

    @seq_task(1)
    def login(self):
        rnum = randrange(len(email_password)-1)
       
        login_data={
                    "login":email_password[rnum][0],
                    "password":email_password[rnum][1],
                    "password_confirmation":email_password[rnum][1]
                   }
        response = self.client.post(url = "/user_ms/auth/sign_in", data=json.dumps(login_data), headers=headers)
        headers ['embibe-token']= response.headers['embibe-token']
        headers ['browser-id']= '1587379640441'
        
    @seq_task(2)
    def Initiating_Session(self):   

        Initial_data = "{\"entityID\":\"null\",\"entityType\":\"primaryOrgId\",\"entityContext\":{\"namespace\":\"embibe\"},\"flagKey\":\"practice_taking\"}"
        response = self.client.post(url = "/flagr/api/v1/evaluation/",name="Initiating_Session", data=Initial_data, headers=headers)
        
    @seq_task(3)
    def Practice_Session(self):
    
  
        PracticeTest_Data = "{\"type\":\"Normal\",\"legacy_session_id\":null,\"learning_map\":{\"exam_code\":\"ex4\",\"goal_code\":\"gl8\",\"subject_code\":null,\"unit_code\":null,\"chapter_code\":null,\"level\":\"exam\",\"goal_slug\":\"engineering\",\"code\":\"lm3\",\"filter_code\":\"\",\"bundle_code\":\"pb6\",\"bundle_version\":1,\"xpath\":\"/jee\"},\"language\":\"en\",\"namespace\":\"embibe\"}"
        
        response = self.client.post(url = "/practice_ms/v1/practice/session/", name="Practice_Session",data=PracticeTest_Data, headers=headers)
        global session_id 
        session_id = response.json().get("session_id","")
        global user_id
        user_id = response.json()["userId"]
        
    @seq_task(4)
    def Practice_Questions(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/question?", name = "Practice_Questions",data = body,headers=headers)
        
    @seq_task(5)
    def Practice_Summary(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/summary", name = "Practice_Summary",data = body,headers=headers)
        
    @seq_task(6)
    def EffortRating(self):
    
        response = self.client.get(url = f"/dsl/er_ms/effort-rating/session/{session_id}", name = "EffortRating",data = body,headers=headers)
        
    @seq_task(7)
    def Skills(self):
    
        Skills_data= "{\"question_codes\":[]}"
    
        response = self.client.post(url ="/content_ms/v2/questions/skills", name = "Skills",data = Skills_data,headers=headers)
        
    @seq_task(8)
    def QuestionCode(self):
    
        response = self.client.get(url ="/content_ms/v2/questions/kt-data?question_code=EM0025943", name = "QuestionCode",data = body,headers=headers)
        
    @seq_task(9)
    def Behavior(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/behavior", name = "Behavior",data = body,headers=headers)
        
    @seq_task(10)
    def Strength(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/strength", name = "Strength",data = body,headers=headers)
        
    @seq_task(11)
    def SessionPack_Recommendation(self):
    
        response = self.client.get(url = "/horizontal_ms/v1/embibe/en/session-pack-recommendation?exam_code=ex4&goal_code=gl8&learning_map=%7B%22chapter_name%22:null,%22goal_code%22:%22gl8%22,%22exam_name%22:%22JEE+Main%22,%22goal_name%22:%22Engineering%22,%22namespace%22:%22embibe%22,%22subject_name%22:null,%22unit_name%22:null,%22exam_code%22:%22ex4%22,%22level%22:%22exam%22,%22code%22:%22lm3%22,%22current_mean_dl%22:1,%22bundle_code%22:%22pb6%22,%22filter_code%22:%22%22,%22bundle_version%22:1,%22type%22:%22Normal%22%7D&attempt_count=0&perfect_count=0&wasted_count=0&overtime_count=0&otc_count=0&oti_count=0", name = "SessionPack_Recommendation",data = body,headers=headers)
     
    @seq_task(12)
    def Session_Check(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/session/{session_id}/check", name = "Session_Check",data = body,headers=headers)
        
    @seq_task(13)
    def Embibe_Guide(self):
    
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/embibeGuide", name = "Embibe_Guide",data = body,headers=headers)
        
    @seq_task(14)
    def Events(self):
    
        Events_data= "[{\"eorder\":1,\"event_type\":\"start_session\",\"sequence\":\"\",\"sent\":false,\"section\":\"\",\"event_info\":\"\",\"t\":1588593424.909,\"question_code\":\"\"},{\"eorder\":2,\"event_type\":\"start_session\",\"sequence\":\"\",\"sent\":false,\"section\":\"\",\"event_info\":\"\",\"t\":1588593431.2695,\"question_code\":\"\"}]"
    
        response = self.client.post(url = f"/practice_ms/v1/practice/{session_id}/events", name = "Events",data = Events_data,headers=headers)
        
    @seq_task(15)
    def QuestionCode_Statistics(self):
              
        response = self.client.get(url = "/horizontal_ms/v1/embibe/en/question-statistics?question_code=EM0025943&exam_code=ex4", name = "QuestionCode_Statistics",data = body,headers=headers)
        
    @seq_task(16)
    def Practice_Questions(self):
              
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/question/EM0025943?version=14&namespace=embibe&language=en", name = "Practice_Questions",data = body,headers=headers)
        
    @seq_task(17)
    def Question_Hint(self):
              
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/question?", name = "Question_Hint",data = body,headers=headers)
        
    @seq_task(18)
    def Question_Pagination(self):
              
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/questions?page=1&pageSize=20", name = "Question_Pagination",data = body,headers=headers)
        
    @seq_task(19)
    def Skip_Question(self):
              
        response = self.client.get(url = f"/practice_ms/v1/practice/{session_id}/question?skipQuestion=true&difficultyLevel=1", name = "Skip_Question",data = body,headers=headers)
        
     
class WebsiteTest(HttpLocust):
    task_set = MyTaskSequence
    wait_time = between(0.5, 5.0)
        

               
              
        

