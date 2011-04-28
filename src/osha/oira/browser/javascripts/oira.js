$("button#report_comment_submit").click(function(event) {
    event.preventDefault();
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
            if (result == true) {
                window.open(url)
            }
            else {
                jQuery('form#report_comment_form').submit();
            }
        }
    ); 
});

$("a#oira_legal_show_hide_anchor").click(function(event) {
    event.preventDefault();
    var anchor = jQuery("a#oira_legal_show_hide_anchor");
    var div = jQuery("div#legal_reference");
    var current_txt = anchor.text() 
    if (current_txt == 'Show') {
        anchor.text('Hide');
        div.show(200);
    }
    else {
        anchor.text('Show');
        div.hide(700);
    }
});
