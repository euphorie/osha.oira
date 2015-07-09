define('nuplone-z3cform', ["jquery", "jquery.browser"], function($) {

var z3cform = {
    getText: function(node) {
        var text="";

        for (var child=node.firstChild; child!==null && child.nodeType===3; child=child.nextSibling)
            text+=child.nodeValue;
        return text;
    },

    setText: function(node, text) {
        var child;
        while (node.firstChild!==null && node.firstChild.nodeType===3)
            node.removeChild(node.firstChild);
        var text_node = document.createTextNode(text);
        if (node.firstChild===null)
            node.appendChild(text_node);
        else
            node.insertBefore(text_node, node.firstChild);
    },

    renumberElement: function (el, attr, i) {
        var $el = $(el),
            buf = $el.attr(attr);
        if (buf) {
            $el.attr(attr, buf.replace(/[0-9]+/, i));
        }
    },

    renumber: function($fieldset) {
        var $fieldsets = $fieldset.children("fieldset"),
            i;
        $(":input:first", $fieldset).val($fieldsets.length);

        for (i=0; i<$fieldsets.length; i++) {
            $("label, :input", $fieldsets[i]).each(function() {
                z3cform.renumberElement(this, "for", i);
                z3cform.renumberElement(this, "id", i);
                z3cform.renumberElement(this, "name", i);
            });
        }
    },

    initialiseExamples: function() {
	$("form :input").each(function() {
	    var selector = /form\.widgets\.(.*)/.exec(this.name);
	    if (selector===null)
		return;
	    selector="#simulation .example-"+selector[1];
	    var $examples = $(selector);
	    if ($examples.length===0)
		return;
	    $(this)
		.focus(function() { $(selector).addClass("focus"); })
		.blur(function() { $(selector).removeClass("focus"); })
		.keyup(function() {
		    var text = this.value;
		    $(selector).each(function() {
			var $this = $(this);
			if (!$this.data("original")) {
			    $this.data("original", z3cform.getText(this));
			    if (!text)
				return;
			}
			if (!text)
			    text=$this.data("original");
			z3cform.setText(this, text);
		    });
		})
		.keyup();
	});
    },

    initialiseMultiwidget: function() {
        $(".multiWidget > button.add").on("click", function() {
            var $button = $(this),
                url = $button.val();
            $.get(url, function(data, status) {
                var $fragment=$(data);
                $button.before($fragment);
                z3cform.renumber($button.parent());
            });
        });

        $(".multiWidget > fieldset > button.remove").on("click", function() {
            var $button = $(this),
                $fieldset = $button.parent(),
                $root = $fieldset.parent();

            $fieldset.remove();
            z3cform.renumber($root);
        });
    },

    onTinyActivate: function(ed) {
        try {
            $("#tinyControls").get(0).contentWindow.activate(ed);
        } catch(e) {
        }

        if (!$("body").hasClass("edit")) {
            $("body").addClass("edit");
        }

    },

    onTinyDeactivate: function(ed) {
        try {
            $("#tinyControls").get(0).contentWindow.deactivate(ed);
        } catch(e) {
        }
    },

    onTinySetup: function(ed) {
        ed.onDblClick.add(function(ed, e) {
            if (e.target.nodeName.toLowerCase()=="a") {
                $("#linkFrame").get(0).contentWindow.show(e.target);
            }
        });

        ed.onActivate.add(z3cform.onTinyActivate);
        ed.onDeactivate.add(z3cform.onTinyDeactivate);
    },

    onFormSubmit: function() {
        $("div.rich.input", this).each(function() {
            var $field = $(this),
                id = $field.attr("id"),
                value = tinyMCE.get(id).getContent(),
                name = $field.data("z3cform.name");
            if (name) {
                $("<input/>")
                    .attr("type", "hidden")
                    .attr("name", name)
                    .val(value)
                    .insertBefore($field);
            }
        });
        return true;
    },

    loadEditorIframes: function() {
        var $wrapper = $("#frameWrapper");

        if (!$wrapper.length) {
            $wrapper=$("<p/>").attr("id", "frameWrapper").appendTo(document.body);
        }

        if (!$("#tinyControls").length) {
            $("<iframe/>")
                .attr("id", "tinyControls")
                .attr("src", plone.context_url+"/@@tiny-controls.html")
                .css("position", "absolute")
                .css("top", "0px")
                .css("left", "0px")
                .css("z-index", "1100")
                .appendTo($wrapper);
        }

        if (!$("#linkFrame").length) {
            $("<iframe/>")
                .attr("id", "linkFrame")
                .attr("src", plone.context_url+"/@@edit-link.html")
                .attr("frameborder", "0")
                .css("z-index", "1100")
                .css("height", "250px")
                .css("width", "510px")
                .css("margin-left", "-255px")
                .css("left", "50%")
                .css("position", "absolute")
                .css("top", "-2000px")
                .css("-webkit-box-shadow", "0 0 15px rgba(0,0,0,0.5)")
                .css("-moz-box-shadow", "0 0 15px rgba(0,0,0,0.5)")
                .css("box-shadow", "0 0 15px rgba(0,0,0,0.5)")
                .appendTo($wrapper);
        }
    },

    // Helper method to deactivate all tiny editors.
    deactivateTiny: function() {
        try {
            tinymce.EditorManager._setActive(null);
            z3cform.onTinyDeactivate();
        } catch (e) {
        }
    },

    doTransforms: function(root) {
        // Replace rich textareas with a div, and activate a tinyMCE editor
        // for them.
        $("textarea.rich", root).each(function() {
            var $textarea = $(this),
                id = $textarea.attr("id"),
                $div = $("<div/>");

            $div
                .attr("id", id)
                .addClass("rich")
                .addClass("input")
                .data("z3cform.name", $textarea.attr("name"))
                .html($textarea.val());
            $textarea.replaceWith($div);
            mapal.initContent($div.parent());
        });
    },

    initialiseRichTextEditor: function(root) {
        if ($("div.rich.input", root).length===0) {
            return;
        }

        z3cform.loadEditorIframes();

        tinyMCE.init({mode: "none",
                      theme: "dummy",
                      element_format: "xhtml",
                      fix_list_elements: true,
                      fix_table_elements: true,
                      entity_encoding: "raw",
                      content_editable: true,
                      forced_root_block: null,
                      setup: z3cform.onTinySetup
                     });

        // Make sure to deactivate tiny when a non-tiny field gets the
        // focus. This will automatically disable the relevant actions
        // in the toolbar.
        $(":input", root).focus(z3cform.deactivateTiny);

        // Deactivate tiny editors after they are added. This guarantees
        // that we receive the correct activate event when the editor gets
        // the focus.
        tinymce.onAddEditor.add(z3cform.deactivateTiny);

        // Replace rich textareas with a div, and activate a tinyMCE editor
        // for them.
        $("div.rich.input", root).each(function() {
            tinyMCE.execCommand("mceAddControl", false, this.id);
        });

        // Check for focus and existing content to determine visibility
        // of any superimposed labels
        $(".rich.input:not(:input)", root).each(function() {
            var $el = $(this),
                $component = $el.closest(".richInput");

            if (!$component.length) {
                return;
            }

            function update() {
                if (mapal.hasContent($el)) {
                    $component.removeClass("empty");
                } else {
                    $component.addClass("empty");
                }
            }

            update();

            $el.bind("focus.z3cform", function() {
                    $component.data("z3cform.timer.rich", setInterval(update, 100));
                })
                .bind("blur.z3cform", function() {
                    update();
                    clearInterval($component.data("z3cform.timer.rich"));
                });
        });

        $("form", root).bind("submit.z3cform", z3cform.onFormSubmit);
    },

    initContent: function(root) {
        z3cform.doTransforms();
        $(window).load(function() {
            z3cform.initialiseRichTextEditor(root);
        });
    },

    init: function() {
        z3cform.initialiseMultiwidget();
        z3cform.initialiseExamples();
    }
};


z3cform.init();
$(document).ready(function() {
    z3cform.initContent();
});

});
/*jslint browser: true, onevar: true, undef: true, regexp: true */

