# Google Summer of Code with GFOSS :sun_with_face: 

**Project:** Creation of a multi user audio first annotation tool

**Mentors:** Pantelis Vikatos, Markos Gogoulos

**Student:** Ioannis Sina

# Introduction

An annotation tool helps people (without the need for specific knowledge) to mark a segment of an audio file (waveform), an image or text etc. in order to specify the segment’s properties. Annotation tools are used in machine learning applications such as Natural Language Processing (NLP) and Object Detection in order to train machines to identify objects or text. While there is a variety of annotation tools, most of them lack the multi-user feature (multiple users annotating a single project simultaneously) whose implementation is planned in this project. The audio annotation process is usually tedious and time consuming therefore, these tools (annotation tools which provide the multi-user feature) are necessary in order to reduce the effort needed as well as to enhance the quality of annotations. Since in most tasks related to audio classification, speech recognition, music detection etc., machine and deep learning models are trained and evaluated with the use audio that has previously been annotated by humans, the implementation of such a tool will lead to higher accuracy of annotated files, as they will have been annotated by more than one human, providing a more reliable dataset. In effect, multi-user annotation will reduce the possibility of human error e.g. an occasional mistaken labelling of a segment might be pointed out by another annotator.

**Already existing annotation tools:**

Label Studio: https://github.com/heartexlabs/label-studio

BAT annotation tool: https://github.com/BlaiMelendezCatalan/BAT

Computer Vision Annotation Tool (CVAT): https://github.com/openvinotoolkit/cvat

# Project goals :dart: 

We will try to develop a web application (audio annotation tool) which will provide the multi-user feature and a pleasant UI for users. There will be three distinct types of users in the application: Managers, Annotators and Reviewers.

**Managers will:**

* Create projects and edit their configurations (title, annotators for each project etc.)
* Upload audio files (links, csv of links or local files) for each project created
* Add/edit labels (labels are used by annotators in order to mark segments of an audio file)
* Assign roles to users (specify who will be annotator or reviewer)
* Export annotations in JSON or CSV format

**Reviewers will:**

* See all annotations done by annotators
* Set annotations as reviewed (completed)
* Add comments to annotations done
* Delete annotations

**Annotators will:**

* Annotate audio files (tasks) assigned  to them (by managers)
* Update annotations
* Submit tasks as annotated
* Skip annotation process (for a specific task)

# Steps to run

Clone repository and cd to the folder
~~~
git clone https://github.com/eellak/gsoc2021-audio-annotation-tool/
cd gsoc2021-audio-annotation-tool
~~~

Create and activate a virtual enviroment
~~~
virtualenv . -p python3
source bin/activate
~~~

Install requirements and cd to label_buddy/
~~~
pip install -r requirements.txt
cd label_buddy
~~~

Make migrations for the Database and all dependencies
~~~
python manage.py makemigrations users projects tasks
python manage.py migrate
~~~

After the above process create a super user and run server
~~~
python manage.py createsuperuser
python manage.py runserver
~~~

Fianlly visit http://localhost:8000/admin and populate Database with data
