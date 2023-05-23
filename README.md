# Social nexus  
 
At first this project was supposed to be like SecureDrop, but I decided to pivot to a sort of social billboard / forum web app. I will definitely remake this to at some point + probably figure out a new name for it

### Current routes 

* **/**: the index. Show posts and has a link to **/dropper**

* **/dropper**: Where to submit posts

* **/post/_id_**: fullpage post. Shows comments and more options and such

* **/comment/_post\_id_**: creates a comment on post. POST method required. redirects to the post after

* **/del/_id_**: delete post with corresponding post id. Requires login and current user must be either the author or admin. redirects to /

* **/del/comment/_post\_id_/_comment\_id_**: delete comment with corresponding comment id. Requires login and current user must be either the author or admin. redirects to /post/*post_id*. 

* **/upvote-post/_id_**: Upvote post with corresponding id. requires login + current user hasnt already liked the post. redirects to post

* **/upvote-comment/_post\_id_/_comment\_id_**: upvote comment with comment_id. requires login + current user hasnt already liked the comment. redirects to post

* **/settings/**: settings page. Requires login

* **/account-delete/**: GET is a form that needs to be filled out to delete an account. POST will delete current_user if the form submits the correct password

* **/pw-change**: GET is a form to change password. POST is to submit the form and change password

* **/profile/_user\_id_**: Profile for a user. Shows all their post and comments. 

### Setup

I use pipenv for virtual environment / pip packages installation.

[Download pipenv](https://pypi.org/project/pipenv/#installation)

And then run pipenv install in this repo's directory and open the env shell:

```
$ pipenv install --dev
$ pipenv shell
```

and set up your secret key:
```
$ touch secretkey.py
$ secretkey=$(python -c 'import secrets; print(secrets.token_hex())')
$ echo "secretkey = '$secretkey'" > secret.py
```
and set up the database by running setupdb.py:
```
$ python setupdb.py
```