define('nuplone-editlink', ["jquery", "jquery.browser"], function($) {

var editlink = {
    // Define these here since IE does not have Node constants
    ELEMENT_NODE: 1,
    TEXT_NODE: 3,

    current_range: null,

    reset: function() {
        $("#external form")[0].reset();
        $("em.message.warning").remove();
    },
    
    hide: function() {
        var topDoc = window.frameElement.ownerDocument;
        $("#linkFrame", topDoc).css({top: "-2000px"});
    },

    show: function(el) {
        var topDoc = window.frameElement.ownerDocument,
            topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,
            selection;

        if (el===undefined) {
            selection=rangy.getSelection(topWindow);
            editlink.current_range=(selection.rangeCount===0) ? null : selection.getRangeAt(0).cloneRange();
            editlink.reset();
        } else {
            editlink.current_range=rangy.createRange(topDoc);
            editlink.current_range.selectNode(el);
            $("input[name=form.widgets.new_window:list]").get(0).checked = (el.target==="_blank");
            $("input[name=form.widgets.URL]").val(el.href);
            $("input[name=form.widgets.title]").val(el.title);
        }

        $("#linkFrame", topDoc).css({top: "70px"});
    },

    removeLink: function() {
        var topDoc = window.frameElement.ownerDocument,
            topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,
            selection = rangy.getSelection(topWindow),
            range, link, found;

        if (selection.rangeCount===0 || selection.isCollapsed)
            return;
        link = selection.anchorNode;
        found=false;
        while (link!==null && !found) {
            if (link.nodeType===editlink.ELEMENT_NODE && link.tagName==="A")
                found=true;
            else
              link=link.parentNode;
        }
        if (!found)
            return;

        var $link = $(link);
        $link.replaceWith($link.contents());
    },

    InsertURL: function(url, title, newwindow) {
        var topDoc = window.frameElement.ownerDocument,
            topWindow = topDoc.defaultView!==undefined ? topDoc.defaultView : topDoc.parentWindow,
            selection = rangy.getSelection(topWindow),
            range, link, found;

        if (editlink.current_range===null)
            return;

        selection.setSingleRange(editlink.current_range);
        if (editlink.current_range.collapsed || !editlink.current_range.canSurroundContents()) {
              link = topDoc.createElement("A");
              link.appendChild(topDoc.createTextNode(title || url));
              editlink.current_range.insertNode(link);
        } else {
          // Try to find a parent link
            link = editlink.current_range.startContainer;
            found=false;
            while (link!==null && !found) {
                if (link.nodeType===editlink.ELEMENT_NODE && link.tagName==="A")
                    found=true;
                else
                  link=link.parentNode;
            }
            if (!found) {
                link = topDoc.createElement("A");
                editlink.current_range.surroundContents(link);
            }
        }
        if (url.indexOf(":")===-1 && url[0]!=="/")
            url = "http://"+url;
        link.href = url;
        link.target = newwindow ? "_blank" : "";
        link.title = title || "";
    },

    init: function() {
        $("button.cancel").on("click", editlink.hide);

        $("button.save").on("click", function() {
            var form = this.form,
                link = form["form.widgets.URL"].value,
                title = form["form.widgets.title"].value,
                newwindow = form["form.widgets.new_window:list"].checked;
            editlink.InsertURL(link, title, newwindow);
            editlink.hide();
        });
    }

};

hide = editlink.hide;
show = editlink.show;
removeLink = editlink.removeLink;
editlink.init();

});

/*jslint browser: true, onevar: true, undef: true, regexp: true */
