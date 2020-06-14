from locust import HttpLocust, TaskSet, TaskSequence, seq_task
from random import randrange
import json
import csv




headers = {
    'embibe-token': ''
}


login_response = {
    "user_id":""
}

mocktest_session = {
    "mocktest_session": {
        "xpath": "/jee-main/chapterwise-test/chemistry/haloarenes",
        "goal_code": "engineering",
        "password": None,
        "source": "offline_app:Aakash--SandwichApp"
    }
}

submit_sync = {
    
}

email_password = []

with open('/locust-tasks/emails_password.csv','r') as file:
    rows = csv.reader(file)
    email_passwords = [row for row in rows]

  

class UserBehavior(TaskSequence):

    @seq_task(1)
    def login(self):
        data = {
            'user[login]': email_passwords[randrange(len(email_passwords)-1)][1],
            'user[password]': email_passwords[randrange(len(email_passwords)-1)][2],
            'app_id': 'Aakash--SandwichApp',
            'pack_type': 'PACK-AAKASH'
        }
        response = self.client.post(url = "/mobile/sandwich_app/login", headers=headers, data=data)
        assert response.json()['success'] == True
        login_response["user_id"] = response.json().get("user_id","")
        headers["embibe-token"] = response.headers["embibe-token"]


    @seq_task(2)
    def fetch(self):
        response = self.client.get(url = f"https://preprodms.embibe.com/content_ms_lt/v1/mobile-application/fetch-app-data?app_id=Aakash--SandwichApp&app_version=4.0.0&user_id={login_response['user_id']}",
        name="https://preprodms.embibe.com/fetch", headers=headers)
        assert response.json()['success'] == True
    
    @seq_task(3)
    def istime(self):
        response = self.client.get(url = f"https://preprodms.embibe.com/content_ms_lt/v1/mocktest-schedules/is-time?xpath={mocktest_session['mocktest_session']['xpath']}&institute_id={856}&branch_id=null&group_id=1004&batch_id=null&key=starts_at&app_id=Aakash--SandwichApp&app_version=4.0.0&user_id={login_response['user_id']}",
        name="https://preprodms.embibe.com/is_time", headers=headers)
        assert response.json()['success'] == True


class WebsiteUser(HttpLocust):
    task_set = UserBehavior