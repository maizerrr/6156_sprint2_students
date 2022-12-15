# 6156_sprint2_students
microservice of students
 - switched to elastic beanstalk
 - implemented CI/CD

## Contributors
Daolong Liu
Yuming Tian

## Endpoint
6156sprint2students-env-2.eba-xmbgar3z.us-east-1.elasticbeanstalk.com

## RESSTful APIs
- /students
  - GET: list all student ids in the database
- /students/{sid}
  - GET: get the detailed information of a student
  - POST: modify the student's profile
  - DELETE: remove the student from the database
- /students/{sid}/courses
  - GET: list all courses the student is enrolled
  - POST: modify/add a course in the student's schedule
  - DELETE: remove a course from the student's schedule
- /students/{sid}/projects
  - GET: list all projects the student is working on
  - POST: modify/add a project in the student's todo list
  - DELETE: remove a project from the student's todo list
- /students/search [not implemented yet]
  - POST: search students with the given query/filter