## App Goals

Game|DB is a primarily Django based project, part of the Code Institute Project Portfolio 4. The aim of this site is to allow users with an interest in gaming a space to discover new games and share their own favourites. The site is intended to foster a community through its use of collections shared by users and by the users being able to interact through the use of reviews/comments.

### Strategy Plane

#### Targeted Users

* Users with an interest in gaming

* Users who want to be part of a community and share their views & gaming interests with others

* Users who would be regularly returning to the site to the contribute to the continued growth of the site

#### Site Goals

* For users to be able to create an account for themselves

* For users to be able to share reviews/comments with others

* For users to be able to create collections of games to share with others

* For users to be able to set their own profile data including personal profile pictures

* To provide up to date information to users when they access the site

#### Project Goals

To provide a site that is both informative and to users who share the same interest and gives the users an incentive to return to the site on a regular basis to foster a sense of community among users through the content they create.

To implement full CRUD functionality which is accessible to standard users accessing the site normally in addition to superusers through the admin site

#### Wireframes

These wireframes showing the initial concepts for the layout of the site were created using Balsamiq, some of the content structure has changed since their original design but the concepts have remained largely the same.

<details>
  <summary>Index Page - Desktop</summary>
  
  ![Index-Page-Desktop](README\wireframe_index_desktop.png)
  
</details>

<details>
  <summary>Index Page - Mobile</summary>
  
  ![Index-Page-Mobile](README\wireframe_home_mobile.png)
  
</details>

<details>
  <summary>Game Description Page - Desktop</summary>
  
  ![Game-Description-Desktop](README\wireframe_game_description_desktop.png)
  
</details>

<details>
  <summary>Game Description Page - Mobile</summary>
  
  ![Game-Description-Mobile](README\wireframe_game_description_mobile.png)
  
</details>

<details>
  <summary>Forms Pages(Signin, Register, Password Change, Profile Change) - Desktop</summary>
  
  ![Forms-Pages-Desktop](README\wireframe_forms_desktop.png)
  
</details>

<details>
  <summary>Forms Pages(Signin, Register, Password Change, Profile Change) - Mobile</summary>
  
  ![Forms-Pages-Mobile](README\wireframe_forms_mobile.png)
  
</details>

<details>
  <summary>Alphabetical List Pages(Genres, Developers, Publishers) - Desktop</summary>
  
  ![Alphabetical-Lists-Desktop](README\wireframe_alphabetical_lists_desktop.png)
  
</details>

<details>
  <summary>Alphabetical List Pages(Genres, Developers, Publishers) - Mobile</summary>
  
  ![Alphabetical-Lists-Mobile](README\wireframe_alphabetical_lists_mobile.png)
  
</details>

<details>
  <summary>Search Result Pages(Search Results, Genres, Developers, Publishers) - Desktop</summary>
  
  ![Search-Results-Desktop](README\wireframe_searches_desktop.png)
  
</details>

<details>
  <summary>Search Result Pages(Search Results, Genres, Developers, Publishers) - Mobile</summary>
  
  ![Search-Results-Mobile](README\wireframe_searches_mobile.png)
  
</details>

<details>
  <summary>Profile Page - Desktop</summary>
  
  ![Profile-Desktop](README\wireframe_profile_desktop.png)
  
</details>

<details>
  <summary>Profile Page - Mobile</summary>
  
  ![Profile-Mobile](README\wireframe_profile_mobile.png)
  
</details>

<details>
  <summary>Reviews & Comments Page - Desktop</summary>
  
  ![Reviews-And-Comments-Desktop](README\wireframe_reviews&comments_desktop.png)
  
</details>

<details>
  <summary>Reviews & Comments Page - Mobile</summary>
  
  ![Reviews-And-Comments-Mobile](README\wireframe_reviews&comments_mobile.png)
  
</details>

<details>
  <summary>Collections Overview Page - Desktop</summary>
  
  ![Collections-Overview-Desktop](README\wireframe_collections_overview_desktop.png)
  
</details>

<details>
  <summary>Collections Overview Page - Mobile</summary>
  
  ![Collections-Overview-Mobile](README\wireframe_collections_overview_mobile.png)
  
</details>

<details>
  <summary>Collection Items Page - Desktop</summary>
  
  ![Collection-Items-Desktop](README\wireframe_collections_desktop.png)
  
</details>

<details>
  <summary>Collection Items Page - Mobile</summary>
  
  ![Collection-Items-Mobile](README\wireframe_collections_mobile.png)
  
</details>

#### Database Construction

Graphviz was used to create the following image showing the database structure and the relationships between the created models.
![Database Visualization](README/models.png)

## Features

### Common Features

#### Navbar
![Navbar-Desktop](README/header_desktop.png)
<details>
  <summary>Navbar Mobile Closed & Expanded</summary>
  
  ![Navbar-Mobile-Closed](README/header_mobile_closed.png)![Navbar-Mobile-Expanded](README/header_mobile_expanded.png)
  
</details>

All pages display a fixed navbar that switches to a hamburger style dropdown menu when viewing on lower resolution devices. This navbar contains links to all current main sub-sections and to the homepage. The logo for the site is included on the navbar and stays even when in responsive modes. To prevent the navbar from becoming overcrowded, the Games section and Profile section when logged in both have separate dropdown menus for their own navigation. When a user is not logged in they are are presented with a Sign-In or Sign-Up option for them to create/access their own account. When logged in these options are replaced by the username of the logged in user.

#### Footer

![Footer-Desktop](README/footer_desktop.png)

<details>
  <summary>Footer Mobile</summary>
  
  ![Footer-Mobile-](README/footer_mobile.png)
  
</details>

Currently the footer uses a split row design to differentiate between site content and informational content. Links to the various site pages are contained in one and could in future be used to also contain social media links for the site. The bottom row of the footer currently contains a simple copyright detail for the site itself. With the site links, they display in a separated grid to give space when viewing on larger displays, switching to a column layout on mobile/tablets.

### Home Page

On a users initial access to the page the first item they will encounter will be the introductory text which gives them an overview of the sites goals. On creation of an account, the logged in user will also be presented with a list of their recently viewed games above this introductory text. For all users they will also be able to see a collection of the most recent reviews left and collections published to the site with links to access the full version of the content selected. Scrolling further down the page they will also be able to see some of the most recently released games and games to be released in the next month which is updated on each visit to the site so as to maintain the most up to date information. On mobile this layout switches to a single column view and reduces the amount of images displayed in the recently viewed, recently released and upcoming image carousels to prevent the images from becoming too small due to the default number displayed on larger devices.

### Genre, Developers, Publishers Lists

These pages provide an alphabetical list of the data available for the sections in question. The alphabetical list at the top of the page links to the specific letter in the page to prevent too much scrolling being needed by the user. After the user selects any of the pages within these sections they will be brought to the item pages described in the following section.

### Search Results, Genre Items, Developer Items, Publisher Items

These above pages follow a similar layout due to their design intent as they are displaying a list of items that the user is searching for depending on their needs. The search results page pulls from the IGDB API and populates the content of the database based on the search while the other pages use the data that has already been retrieved to populate those pages. The search results page will return the thumbnail for the cover of the game searched for along with the name of the game along with a link to its description page. In addition to the previous data, the genre,developer and publisher item pages will also return the average review score for the games present based on user reviews and the total number of reviews that have been left for a game that have been used to calculate that average.

### Game Description Page

The top half of the page contains all the information on the game the user has selected as seen in the above screenshot. When a user has logged in they also have the option to add the game to their personal collection or to add it to a created collection if they have created any and if the game is already part of a collection/s they will also have the option to remove it from the collection they choose. Below the game information, any reviews left will be displayed along with the option to display any comments if they have been left on a review. For a logged in user they will also be given the option to leave a review/reply to a comment and in addition to this if a user is already an author of a review/comment they will be given the option to edit/delete that content. If they choose to delete a comment, they will be prompted with a pop-up window asking them to confirm the deletion. If the user chooses to leave a review/comment the form field expands to show the text input fields including the text editor for comments/reviews.

### Profile Page

The users profile page contains their current profile information and profile picture if set or the default image if not. From here a user can access the content they've created for the site such as their reviews/comments, lists or personal collection. They can also update their profile picture and have options to update their password and profile data. 

### Reviews & Comments

This page uses a tabbed display to show any reviews or comments left by a user which can be switched between at will. These tabs show the name along with the link to the game, their rating, comments and title for the content as well. These tables are both set to paginate at 10 items to avoid the page becoming overly long and when on mobile devices the review table collapses to prevent horizontal scrolling.

#### Sign-In, Sign-Up & Password Change Pages

These pages all use a similar design concept and use the same functionality to process the user data. These forms will advise the user of the requirements for the action they wish to take and will be prompted with error messages if they provide incorrect/invalid data. When being processed they use Django's inbuilt authentication functionality to process these requests and work with the User model to update/create the data for the user.

#### Profile Update

Here the user can update certain information from their profile and have it reflected in their profile page.

#### My Collections

Here a user can see all the collections they have made for the site and create new lists for sharing among users of the site itself. After creating a collection, the collection will be in draft mode until at least one item is contained within the collection at which point a user can choose to publish this to the site itself for others to view. Once published they will also have the option to unpublish it or to delete it fully from the site itself.

#### Personal Collections

A user can add games to their own personal collection which is only visible to themselves and the intention is for this to be used by people setting up a backlog or collecting a list of what they own without needing to assign it to a specific collection

#### Error Pages

A collection of error pages(404, 500, 503) were created for the site and display when the user encounters the specific issue that the error specifies and they are provided with an error image, an explanation of the issue and a link back to the Homepage of the site.


### Colour Palette

![Colour Palette](README/colours.webp)
For this project I decided on a simple dark colour design with a limited number of colours as shown in the above colour palette. I've avoided using pure black in the header and footer as per Material Design recommendations and using the dark gray #121212 in its place. Similarly I'm using the off-white shade #EEEEEE for the general text in place of pure white. The choices of #1F2933 and #212529 are used in contrast to the general page background colour of #241C2C and help to give a sense of elevation and distinguish between elements.

### Typography

For the Navbar I've chosen to use Bruno Ace SC as a semi-futuristic style of font in keeping with the gaming theme of the website. With the remainder of the content, I've chosen to use Ubuntu Light for the text due to its light and simple nature and readability.

## Technologies Used

[Python](https://www.python.org/) - Main language used in the project for all aspects

[Django](https://www.djangoproject.com/) - Python framework used for developing the application

[HTML](https://en.wikipedia.org/wiki/HTML) - Used for designing all the page content

[CSS](https://en.wikipedia.org/wiki/CSS) - Used for styling content displayed to end users

[Javascript](https://www.javascript.com/) - Used for some of the interactive content and formatting of certain pages

[AWS](https://aws.amazon.com/) - Used for hosting the media & static files and also for hosting the PostgreSQL database

[PostgreSQL](https://www.postgresql.org/) - Used for the model databases

[Diagrams.net](https://www.diagrams.net/) - Used to design the flowchart in the README file

[Heroku](https://www.heroku.com/) - For deploying the finished code

[Gunicorn](https://gunicorn.org/) - Python based HTTP server used in deployment of final code

### Libraries & Frameworks

[Bootstrap](https://getbootstrap.com/) - Used for quicker styling of certain elements

[TinyMCE](https://www.tiny.cloud/) - Allows embedding of rich text editor within content allowing users to style their reviews/comments

[jQuery](https://jquery.com/) - Used for running certain Javascript content

[Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html) - Used to integrate AWS S3 bucket for content upload and retrieval

[Crispy Forms](https://django-crispy-forms.readthedocs.io/en/latest/) - Django library to assist in the rendering of forms within templates

[Django Widget Tweaks](https://pypi.org/project/django-widget-tweaks/) - Used to extend the options available with regards to form fields within templates in order to add attributes

[Pillow](https://pillow.readthedocs.io/en/stable/) - Python image library used for conversion and assignment of image files

[Psycopg2](https://pypi.org/project/psycopg2/) - Python database connector used to connect with PostgreSQL database

[Django Resized](https://pypi.org/project/django-resized/) - Used to resize images for saving to S3 bucket

[DataTables](https://datatables.net/) - jQuery plugin used to paginate the content in the tabbed pages of the My Reviews & Comments page

[Slick](https://kenwheeler.github.io/slick/) - Slider used for image carousels on home page

[Star Rating](https://plugins.krajee.com/star-rating) - jQuery plugin used for the hoverable star rating option when leaving a reviews/comments

### Resources

[Graphviz](https://graphviz.org/) - Used to create the representation of the database structure and its relationships

[IGDB](https://www.igdb.com/) - API used to retrieve content for populating of application

[MDN](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django) - Used as tutorial on Django set upload

[CDNFonts](https://www.cdnfonts.com/) - Used for the custom fonts used in the project

[W3Schools](https://www.w3schools.com/python/default.asp) - General documentation on Python syntax

[PyPI](https://pypi.org/) - Used for finding specific Python/Django libraries to meet the project needs
