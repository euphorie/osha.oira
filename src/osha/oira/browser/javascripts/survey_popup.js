jQuery.cookie = function(name, value, options) {
    /* Copyright (c) 2006 Klaus Hartl */
    if (typeof value != 'undefined') { // name and value given, set cookie
        options = options || {};
        if (value === null) {
            value = '';
            options.expires = -1;
        }
        var expires = '';
        if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) {
            var date;
            if (typeof options.expires == 'number') {
                date = new Date();
                date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000));
            } else {
                date = options.expires;
            }
            expires = '; expires=' + date.toUTCString(); // use expires attribute, max-age is not supported by IE
        }
        // CAUTION: Needed to parenthesize options.path and options.domain
        // in the following expressions, otherwise they evaluate to undefined
        // in the packed version for some reason...
        var path = options.path ? '; path=' + (options.path) : '';
        var domain = options.domain ? '; domain=' + (options.domain) : '';
        var secure = options.secure ? '; secure' : '';
        document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join('');
    } 
    else { // only name given, get cookie
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
};

function oc(a) {
    // Thanks to Jonathan Snook: http://snook.ca
    var o = {};
    for(var i=0; i<a.length; i++) {
        o[a[i]]='';
    }
    return o;
}

$("button#report_comment_submit").click(function(event) {
    /* If the user agrees to do the survey, we add him to a cookie and won't
     * bother again.
     */
    var tool_url = window.location.pathname;
    var cookie = jQuery.cookie('survey_ignore', undefined, {path: tool_url});
    var usernames = Array();
    if (cookie) { 
        usernames = cookie.split('|'); 
    }
    var username = jQuery("p#username").text();
    if (username in oc(usernames)) {
        return;
    }
    event.preventDefault();
    usernames.push(username);
    jQuery.cookie('survey_ignore', usernames.join('|'), {path: tool_url});

    var heading = jQuery("#survey_popup_title").text();
    var text = jQuery("#survey_popup_text").text();
    var ok = jQuery("#survey_popup_confirm").text();
    var cancel = jQuery("#survey_popup_deny").text();
    var url = jQuery("#survey_popup_url").text();
    $.alerts.okButton = '&nbsp;'+ok+'&nbsp;';
    $.alerts.cancelButton = '&nbsp;'+cancel+'&nbsp;';
    jConfirm(
        text, 
        heading, 
        function(result) {
            if (result === true) {
                window.open(url);
            }
            jQuery('form#report_comment_form').submit();
        }
    ); 
});
