# Social nexus  
 
At first this project was supposed to be like SecureDrop, but I decided to pivot to a sort of social billboard / forum web app. I will definitely remake this to at some point + probably figure out a new name for it

### Current routes (out of date)

* **/**: the index. Has a link to the dropper and recipient pages and login/signin page

* **/login**: Login page. needs a user name and a password candidate

* **/signup**: make a new user account

* **/logout**: will logout current user. requires login

* **/dropper**: Where to make posts. Basically a form with a textbox right now. requires login

* **/recipient**: where to see all the posts

* **/delete/_id_**: api request thingy to delete the post with the corresponding id. Requires login and will only work if current_user is the author of the post

* **/delete/comment/_post id_/_comment id_**: delete comment with that id. Redirects to /post/_post id_ . Requires login and will only work if current_user is the author of the post

* **/upvote-post/_post id_/**: upvote post with _post id_

* **/upvote-comment/_post id_/_comment id_**: increments comment vote cell by 1

* **/post/_id_**: returns full page post with comments and extra options

* **/comment/_post\_id_**: POST a comment on post with _post\_id_