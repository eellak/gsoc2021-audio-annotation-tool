# :information_source: Project info 

### Brief explanation
**Label Buddy** is powered by [GFOSS](https://gfoss.eu/) and [GSoC](https://summerofcode.withgoogle.com/). It is an audio labeling tool which features 3 types of users: Managers, annotators and reviewers. The distinction between the user roles is what makes Label Buddy unique. A Detailed explanation of Label Buddy can be found [here](https://github.com/eellak/gsoc2021-audio-annotation-tool/blob/main/README.md).

### Important links
* GitHub repository: https://github.com/eellak/gsoc2021-audio-annotation-tool
* GitHub README.md link: https://github.com/eellak/gsoc2021-audio-annotation-tool/blob/main/README.md
* Label Buddy demo link: https://labelbuddy.io/

### Important pull requests
* Merge dev_branch with main: [#25](https://github.com/eellak/gsoc2021-audio-annotation-tool/pull/25)
* Merge review_page with main: [#31](https://github.com/eellak/gsoc2021-audio-annotation-tool/pull/31)

### Tech Stack
* Django, Django templates, Python
* HTML, css, js


# :heavy_check_mark: Tasks completed during GSoC (7 JUNE - 16 AUGUST)
[Here](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues?q=is%3Aissue+is%3Aclosed) you can see all issues closed during the coding period. Each issue has a brief explanation of what should be done. In every issue you can see every commit done for it. Now let's list the **most important** tasks (issues) for Label Buddy and show some screenshots of completed tasks.

## 1. Create django models
* Related issues: [#1](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/1), [#2](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/2), [#3](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/3)
* Working branch: [main](https://github.com/eellak/gsoc2021-audio-annotation-tool)
* **Task**: Created Django models: User, Project, Task, Annotation, Comment, Label. Users will be managers, annotators and reviewers. If can_create_projects variable is set to true user can create projects, add labels and import tasks (audio files). Annotators can create annotations for tasks and reviewers can create reviews for completed annotations

## 2. Login/Register
* Related issue: [#12](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/12)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Created basic Login/Register system. For the backend of this task I used [django-allauth](https://django-allauth.readthedocs.io/en/latest/installation.html)

#### Login
![Login](https://user-images.githubusercontent.com/49285637/130133546-1adfb7cf-c2cd-47ff-8299-e14fb67746b7.png)

#### Register
![Register](https://user-images.githubusercontent.com/49285637/130133616-8f9c6664-b8d5-4bc7-a171-c0b709718e1a.png)

## 3. Index page
* Related issue: [#13](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/13)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create index page in which the user will be able to see all projects that he/she is involved in. A user is involved in a project if he/she is a manager an annotator or a reviewer

#### Index page
![Index_page](https://user-images.githubusercontent.com/49285637/130134367-7aa146eb-99f4-453d-9d34-9bb5f67b8ef8.png)

## 4. User creates project
* Related issue: [#14](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/14)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for creating projects. User can specify all project's attributes like title, labels, annotators etc

#### Project create page
![project_create_page](https://user-images.githubusercontent.com/49285637/130134829-d6f51827-b440-4ca9-bd9e-56a9617f1c18.png)

## 5. User edits project
* Related issue: [#15](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/15)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for editing projects. **Only** managers of a project can edit it

#### Project edit page
![project_edit_page](https://user-images.githubusercontent.com/49285637/130135153-910841f5-8bb8-4f72-96f7-1c199235c2d1.png)

## 6. Add tasks to project
* Related issue: [#16](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/16)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Managers can import single audio files (.wav, .mp3 and .mp4) or .zip files containing accepted format files. Every audio file represent a task for the project which needs to be annotated

#### Import data page
![Import_data](https://user-images.githubusercontent.com/49285637/130135692-69e6632e-f46f-4ca1-95a9-ce6b2f1d8cc5.png)

## 7. List tasks for project
* Related issue: [#17](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/17)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create a page for listing tasks for annotation/review. Tasks displayed depend on the user's role in the project. Managers can see all task uploaded. Annotators can see only tasks assigned to them and reviewers can see all tasks in order to review them

#### Project page **before** importing data
![Project_page_before_import](https://user-images.githubusercontent.com/49285637/130136446-1a075f56-1afc-48ef-9fe5-24fd3737cabe.png)

#### Project page **after** importing 10 audio files
![Project_page_after_import](https://user-images.githubusercontent.com/49285637/130136484-a8d2f72f-08fd-496e-8ac4-4793af940b21.png)

## 8. Annotate tasks for project
* Related issue: [#18](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/18)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Create annotation page where annotators will be able to annotate a task. They are able to drug and create regions on the waveform and label them with the project's labels

#### Annotation page **before** creating an annotation
![Annotation_page_before_annotation](https://user-images.githubusercontent.com/49285637/130137165-9de6e903-cb9e-41c7-baf9-50220a9bb3e5.png)

#### Annotation page **after** creating an annotation
![Annotation_page_after_annotation](https://user-images.githubusercontent.com/49285637/130137175-052d0cbf-0d70-40cc-9320-7126d7a1a28e.png)

## 9. Review tasks for project
* Related issue: [#19](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/19)
* Working branch: [review_page](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/review_page)
* **Task**: Create review page where a reviewer can comment an annotation and either Approve it or Reject it

#### Review page **before** creating a review
![Review_page_before_review](https://user-images.githubusercontent.com/49285637/130137748-c8b8f2f6-1161-4663-8110-4b71a6d00691.png)

#### Review page **after** creating a review
![Review_page_after_review](https://user-images.githubusercontent.com/49285637/130137805-0515e932-2dae-43fd-8dbd-f45e179a1cfa.png)

## 10. Export annotations for project
* Related issue: [#20](https://github.com/eellak/gsoc2021-audio-annotation-tool/issues/20)
* Working branch: [dev_branch](https://github.com/eellak/gsoc2021-audio-annotation-tool/tree/dev_branch)
* **Task**: Managers are able to export all annotations completed for a project in JSON or CSV format. They can export either Approved annotations or all of them

#### Export data page
![Export_data_page](https://user-images.githubusercontent.com/49285637/130138221-b79f7cbf-19a2-4929-a687-b56ae7d86674.png)

## Some other pages

#### List annotations for reviewers to choose
![List_annotations_page](https://user-images.githubusercontent.com/49285637/130138543-cc8a9a88-e886-4b6b-b8d7-6c30e40d2b37.png)

#### Annotation page after annotation reviewed
![Annotation_page_after_review](https://user-images.githubusercontent.com/49285637/130138650-94f9740b-e8dd-40bd-8883-2a1f175d84e0.png)

#### User edit profile page
![Edit_profile](https://user-images.githubusercontent.com/49285637/130138844-fad51340-41c3-4b86-913b-24fb538c59d2.png)




# :white_check_mark: Task Left to Do
* UX imporvements: https://www.figma.com/file/gUelQicOdfJkrqs2XJvHl5/Label-Buddy?node-id=214%3A2605
* Rar file upload. Zip is already accepted
* Swagger documentation
* Use exported data for machine learning models

# :blush: Acknowledgements

First and foremost, thanks to my mentors, **Pantelis Vikatos** and **Markos Gogoulos** for guiding and giving me useful advice for the project. It was a pleasure working with them and I hope I get the opportunity to do it again soon. Moreover I would like to thank the Design team (names here) for the UX suggestions which can be found [here](https://www.figma.com/file/gUelQicOdfJkrqs2XJvHl5/Label-Buddy?node-id=214%3A2605).

