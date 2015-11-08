# Python-bookmarks
##### Flask app for saving Python related urls


/bookmarks/ endpoints:

```
/bookmarks/ (Get all bookmarks)

/bookmarks/<title>/update (Update bookmark by specifying title, login required)
/bookmarks/<title>/vote (Vote a bookmark according to <title>, login required)

/bookmarks/categories (Get all categories)
/bookmarks/categories/<name> (Get bookmarks by category <name>)

/bookmarks/import (Import bookmarks, login required)
```

/categories/ endpoints:

```
/categories (Get all categories)
/categories/name (Get all bookmarks by specifying category name)
```

/users/ enpoints

```
/users/ (Get all users)
/users/<username> (Get user profile according to <username>)

/users/<username>/bookmarks/ (Get user's bookmarks according to <username>)
/users/<username>/bookmarks/<title> (Get user's bookmark according to <username> and bookmark <title>)

/users/<username>/bookmarks/add (Add a new bookmark, login required)

/users/<username>/categories (Get user's categories by specifying username)
/users/<username>/categories/<name> (Get user's bookmarks by specifying username and category name)
```

Auth endpoints:
```
/login
/logout (Login required)
/register
```
