$("button#report_comment_submit").click(function(event) {
    event.preventDefault();
    var heading = jQuery("#survey_popup_title").text();
    var text = jQuery("#survey_popup_text").text();
    var ok = jQuery("#survey_popup_confirm").text();
    var cancel = jQuery("#survey_popup_deny").text();
    $.alerts.okButton = '&nbsp;'+ok+'&nbsp;';
    $.alerts.cancelButton = '&nbsp;'+cancel+'&nbsp;';
    jConfirm(
        text, 
        heading, 
        function(result) {
            if (result == true) {
                window.location.replace('http://www.surveymonkey.com/s/OiRATool')
            }
            else {
                jQuery('form#report_comment_form').submit();
            }
        }
    ); 
});
