function sendVote(bookmark_title, vote, loop_index) {
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
   $.ajax({
        url: '/bookmarks/' + encodeURIComponent(bookmark_title) + '/vote',
        data: JSON.stringify({'vote': vote}),
        type: 'POST',
        contentType: 'application/json;charset=UTF-8',
        success: function (new_rating) {
            var total_votes = document.getElementById("total_vote_" + loop_index);
            total_votes.innerHTML = "<strong>" + new_rating + "</strong>";
        },
        error: function (xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function vote(loop_index, vote) {
    var orange = 'rgb(255, 102, 0)';
    var upvote = document.getElementById("up_vote" + loop_index);
    var downvote = document.getElementById("down_vote" + loop_index);
    var bookmark_title = document.getElementById("title_" + loop_index).innerText;

    if (vote === 1) {
        if (upvote.style.color === orange) {  // Reset vote
            upvote.style.color = ''
        } else if (downvote.style.color === orange) {  // From down to up
            upvote.style.color = orange
            downvote.style.color = ''
        } else {  // New upvote
            upvote.style.color = orange
        }
        sendVote(bookmark_title, vote, loop_index)

    } else if (vote === -1) {
        if (downvote.style.color === orange) {  // Reset vote
            downvote.style.color = ''
        } else if (upvote.style.color === orange) {  // From up to down
            upvote.style.color = ''
            downvote.style.color = orange
        } else {  // New downvote
            downvote.style.color = orange
        }
        sendVote(bookmark_title, vote, loop_index)
    }
}
