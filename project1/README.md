# Project 1 - BookieWookie - Book Review Site

"/" + "/search" - home and search pages - Both have a simple form allowing user to search for books, but the design is different. If no search results are found an error message is displayed, else a list of results is displayed. The search queries all fields of the book (isbn, author, title) and displays all partial matches/substrings.

"/login" "/register" - User can log in and create an account here.

"books/?isbn=" - Page where book information and reviews are displayed - Page is split into 2 columns, 1 displaying the book info and form for writing a review. 1 showing the ratings from the goodbooks website using their api and reviews from users of this site. If the user is not logged in they are shown a log in form instead of the review writing form. After they log in they are directed back to the page where the form is now visible. There is a slider for setting the review score /5 and a text area which must have a minimum of 100 characters before submitting, the amount of characters currently written is displayed to the user. If the review is less than 100 characters or the user forgets to set a review score the review will not be submitted. Also if the user has already written a review for the book they are not allowed to submit another.

"api/{isbn}" - API that returns the average review score and count of books on this site. If isbn is not in the database a 404 error is shown.
