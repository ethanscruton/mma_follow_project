/* Follow and unfollow buttons */
$('.follow-btn').click(function(){
    var fid;
    fid = $(this).attr('data-fid');
    attr_id = '#follow-btn-'.concat(fid);
    $.get('/upcoming-fights/follow/', {fighter_id: fid})
    location.reload()
});

$('.unfollow-btn').click(function(){
    var fid;
    fid = $(this).attr('data-fid');
    attr_id = '#unfollow-btn-'.concat(fid);
    $.get('/upcoming-fights/unfollow/', {fighter_id: fid})
    location.reload()
});

/* Search 
$('.search-btn').click(function(){
    var query;
    query = $(this).val();
    $.get('/upcoming-fights/search-fighters/', {suggestion: query})
});
*/