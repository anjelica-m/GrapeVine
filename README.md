CMPUT404-project-socialdistribution
===================================

CMPUT 404 Project: Social Distribution

[Project requirements](https://github.com/uofa-cmput404/project-socialdistribution/blob/master/project.org) 

[Project wiki](https://github.com/uofa-cmput404/404f23project-restless-clients/wiki)

[Project Demonstration Video](https://youtu.be/X0vkAN03SjE)

Contributors / Licensing
========================

Authors:
    
* Kai Luedemann
* Anjelica Marianicz
* James Schaefer-Pham
* Sashreek Magan
* Shalomi Hron

Generally everything is LICENSE'D under the MIT license.

## Project Setup Frontend

```sh
cd frontend
npm install
npm run build
```
## Project Setup Backend

```sh
cd socialDistribution
python manage.py runserver
```

Deployment Link
===============
[Deployed App](https://restlessclients-7b4ebf6b9382.herokuapp.com/) [No longer deployed]

All User Stories (with ✓ are completed)
=======================================
- As an author I want to make public posts. ✓
- As an author I want to edit public posts. ✓
- As an author, posts I create can link to images.
- As an author, posts I create can be images. ✓
- As a server admin, images can be hosted on my server. ✓
- As an author, posts I create can be private to another author
- As an author, posts I create can be private to my friends
- As an author, I can share other author’s public posts
- As an author, I can re-share other author’s friend posts to my friends
- As an author, posts I make can be in simple plain text ✓
- As an author, posts I make can be in CommonMark ✓
- As an author, I want a consistent identity per server ✓
- As a server admin, I want to host multiple authors on my server ✓
- As a server admin, I want to share public images with users on other servers. 
- As an author, I want to pull in my github activity to my “stream” ✓
- As an author, I want to post posts to my “stream” ✓
- As an author, I want to delete my own public posts. ✓
- As an author, I want to befriend local authors ✓
- As an author, I want to befriend remote authors
- As an author, I want to feel safe about sharing images and posts with my friends – images shared to friends should only be visible to friends. [public images are public]
- As an author, when someone sends me a friends only-post I want to see the likes.
- As an author, comments on friend posts are private only to me the original author.
- As an author, I want un-befriend local and remote authors
- As an author, I want to be able to use my web-browser to manage my profile
- As an author, I want to be able to use my web-browser to manage/author my posts
- As a server admin, I want to be able add, modify, and remove authors. ✓
- As a server admin, I want to OPTIONALLY be able allow users to sign up but require my OK to finally be on my server ✓
- As a server admin, I don’t want to do heavy setup to get the posts of my author’s friends. ✓
- As a server admin, I want a restful interface for most operations ✓
- As an author, other authors cannot modify my public post ✓
- As an author, other authors cannot modify my shared to friends post. ✓
- As an author, I want to comment on posts that I can access ✓
- As an author, I want to like posts that I can access ✓
- As an author, my server will know about my friends ✓
- As an author, When I befriend someone (they accept my friend request) I follow them, only when the other author befriends me do I count as a real friend – a bi-directional follow is a true friend.
- As an author, I want to know if I have friend requests. ✓
- As an author I should be able to browse the public posts of everyone ✓
- As a server admin, I want to be able to add nodes to share with ✓
- As a server admin, I want to be able to remove nodes and stop sharing with them. ✓
- As a server admin, I can limit nodes connecting to me via authentication. ✓
- As a server admin, node to node connections can be authenticated with HTTP Basic Auth ✓
- As a server admin, I can disable the node to node interfaces for connections that are not authenticated! ✓
- As an author, I want to be able to make posts that are unlisted, that are publicly shareable by URI alone (or for embedding images)


Resources / Citations
======================

* [Signals](https://docs.djangoproject.com/en/4.2/topics/signals/)
* [CSS Rounded](https://www.w3schools.com/css/css3_borders.asp)
* [Linking externally](https://stackoverflow.com/questions/11759028/changing-base-url-on-part-of-a-page-only) by [Sablefoste](https://stackoverflow.com/users/1408137/sablefoste)
* [List styling](https://www.w3schools.com/cssref/pr_list-style-type.php)
* [CSS Rounded Buttons](https://www.w3schools.com/howto/howto_css_round_buttons.asp)
* [Django Rest Framework Docs](https://www.django-rest-framework.org/)
* [Django Docs](https://docs.djangoproject.com/en/4.2/)
