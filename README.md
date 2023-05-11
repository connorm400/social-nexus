# Social nexus  
 
At first this project was supposed to be like SecureDrop, but I decided to pivot to a sort of social billboard / forum web app. I will definitely remake this to at some point + probably figure out a new name for it

### Current routes

* **/**: the index. Has a link to the dropper and recipient pages

* **/dropper**: Where to make posts. Basically a form with a textbox right now

* **/recipient**: where to see all the posts

* **/delete/_id_**: api request thingy to delete the post with the corresponding id

* **/delete/comment/_post id_/_comment id_**: delete comment with that id

* **/upvote-post/_post id_/_comment id_**: increments post's vote cell by 1

* **/post/_id_**: GET is fullpage for a post. 
     * POST is for submitting a comment