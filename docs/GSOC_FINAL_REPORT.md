# :information_source: Project info 

![facebook_cover_photo_1](https://user-images.githubusercontent.com/49285637/130322348-a232336f-c4cf-4c1e-8c77-b7e5a27fa108.png)

### Brief explanation
**Label Buddy** is powered by [GFOSS](https://gfoss.eu/) and [GSoC](https://summerofcode.withgoogle.com/). It is an audio labeling tool which features 3 types of users: Managers, annotators and reviewers. The distinction between the user roles is what makes Label Buddy unique. A Detailed explanation of Label Buddy and steps for installation can be found [here](https://github.com/eellak/gsoc2021-audio-annotation-tool/blob/main/README.md).

### Important links
* GitHub repository: https://github.com/eellak/gsoc2021-audio-annotation-tool
* GitHub README link: https://github.com/eellak/gsoc2021-audio-annotation-tool/blob/main/README.md
* Label Buddy demo link: Go to https://labelbuddy.io/ and sign in with the following credentials in order to check out Label Buddy:
  * **Username**: demo
  * **Password**: labelbuddy123

[**Here**](https://github.com/eellak/gsoc2021-audio-annotation-tool/blob/main/docs/user_manual.md) you will find a user manual with screenshots and explanations for Label Buddy

### Important pull requests
* Merge dev_branch with main: [#25](https://github.com/eellak/gsoc2021-audio-annotation-tool/pull/25)
* Merge review_page with main: [#31](https://github.com/eellak/gsoc2021-audio-annotation-tool/pull/31)

### Tech Stack
* Django, Django templates, Python
* HTML, css, js


# :heavy_check_mark: Tasks completed during GSoC (7 JUNE - 16 AUGUST)
[Here](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues?q=is%3Aissue+is%3Aclosed) you can see all issues closed during the coding period. Each issue has a brief explanation of what should be done. In every issue you can see every commit done for it. Now let's list the **most important** tasks (issues) for Label Buddy.

## 1. Create django models
* Related issues: [#1](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/1), [#2](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/2), [#3](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/3)
* Working branch: [main](https://github.com/eellak/gsoc2021-audio-annotation-tool)
* **Task**: Created Django models: User, Project, Task, Annotation, Comment, Label. Users will be managers, annotators and reviewers. If can_create_projects variable is set to true user can create projects, add labels and import tasks (audio files). Annotators can create annotations for tasks and reviewers can create reviews for completed annotations

## 2. Login/Register
* Related issue: [#12](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/12)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Created basic Login/Register system. For the backend of this task I used [django-allauth](https://django-allauth.readthedocs.io/en/latest/installation.html)

## 3. Index page
* Related issue: [#13](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/13)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create index page in which the user will be able to see all projects that he/she is involved in. A user is involved in a project if he/she is a manager an annotator or a reviewer

## 4. User creates project
* Related issue: [#14](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/14)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for creating projects (if user has the permission) . User can specify all project's attributes like title, labels, annotators etc

## 5. User edits project
* Related issue: [#15](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/15)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for editing projects. **Only** managers of a project can edit it

## 6. Add tasks to project
* Related issue: [#16](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/16)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Managers can import single audio files (.wav, .mp3 and .mp4) or .zip files containing accepted format files. Every audio file represent a task for the project which needs to be annotated

## 7. List tasks for project
* Related issue: [#17](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/17)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for listing tasks for annotation/review. Tasks displayed depend on the user's role in the project. Managers can see all task uploaded. Annotators can see only tasks assigned to them and reviewers can see all tasks in order to review them

## 8. Annotate tasks for project
* Related issue: [#18](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/18)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create annotation page where annotators will be able to annotate a task. They are able to drug and create regions on the waveform and label them with the project's labels

## 9. Review tasks for project
* Related issue: [#19](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/19)
* Working branch: [review_page](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/review_page)
* **Task**: Create review page where a reviewer can comment an annotation and either Approve it or Reject it

## 10. Export annotations for project
* Related issue: [#20](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/20)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Managers are able to export all annotations completed for a project in JSON or CSV format. They can export either Approved annotations or all of them
* Examples of exported files can be found [here](https://drive.google.com/drive/folders/1aQqYuO4czitTEFcDNjBsqc99zewMeW2r?usp=sharing)

# :white_check_mark: Task Left to Do
* UX imporvements: https://www.figma.com/file/gUelQicOdfJkrqs2XJvHl5/Label-Buddy?node-id=214%3A2605
* Rar file upload. Zip is already accepted
* Swagger documentation
* Use exported data for machine learning models

# :blush: Acknowledgements

First and foremost, I want to thank my mentors [**Pantelis Vikatos**](https://www.linkedin.com/in/pantelis-vikatos-1383437a/) and [**Markos Gogoulos**](https://github.com/mgogoulos), for guiding, giving me useful advice for the project and helping me whenever I faced an issue. It was a pleasure working with them and I hope I get the opportunity to do it again soon. We had a meeting twice a week and our means of communication was **[Mattermost](https://mattermost.com/)**. Moreover I would like to thank **Jen Anastasopoulou** and **Lina Aggelopoulou** for the UX improvements which can be found [here](https://www.figma.com/file/gUelQicOdfJkrqs2XJvHl5/Label-Buddy?node-id=214%3A2605). These improvements will have been applied by the end of the month and will make Label Buddy more user friendly. Finally, I would like to express my appreciation to **[Orfium](https://www.orfium.com/)** for supporting the whole project from the start to the end of it. 
