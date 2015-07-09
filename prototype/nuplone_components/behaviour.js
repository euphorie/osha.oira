/** Markup Pattern Library.
 *
 * Copyright 2009-2011 W. Akkerman
 */

/*jslint browser: true, undef: true, eqeqeq: true, regexp: true */

define('nuplone-behaviour', ["jquery", "jquery.browser"], function($) {

var mapal = {
    widthClasses: {},

    // Utility methods
    registerWidthClass: function(cls, minimum, maximum) {
        mapal.widthClasses[cls] = { minimum: minimum,
                                    maximum: maximum };
    },

    _renumberAttribute: function(el, attr, i) {
        var $el = $(el),
            buf = $el.attr(attr);
        if (buf) {
            $el.attr(attr, buf.replace(/[0-9]+/, i));
        }
    },

    renumber: function($container, selector) {
        var $entries = $container.find(selector ? selector : "fieldset,tr,dd"),
            entry, i;
        var _renumber = function() {
            mapal._renumberAttribute(this, "for", i);
            mapal._renumberAttribute(this, "id", i);
            mapal._renumberAttribute(this, "name", i);
        };
        for (i=0; i<$entries.length; i++) {
            entry = $entries.get(i);
            mapal._renumberAttribute(entry, "id", i);
            $("label, :input", entry).each(_renumber);
        }
    },

    // Give the first input element with the autofocus class the focus
    initAutofocus: function(root) {
        var $elements = $(":input.autofocus", root), i;

        for (i=0; i < $elements.length; i+=1) {
            if (!$elements.eq(i).val()) {
                $elements.get(i).focus();
                break;
            }
        }
        if (i===$elements.length) {
            $elements.eq(0).focus();
        }
    },

    // A simple autocomplete pattern
    initAutocomplete: function(root) {
          $("input.autocomplete", root).each(function() {
              var $input = $(this), 
                  name = $input.attr("name"),
                  $storage;
              $input.attr("name", "_"+name);
              $storage=$("<input type='hidden'/>").attr("name", name).insertBefore($input);
              $input.autocomplete({source: $input.attr("src"),
                                   minLength: 2,
                                   select: function(event, ui) { 
                                        $storage.val(ui.item.value);
                                        $input.val(ui.item.label);
                                        return false;
                                   }
                                   });
          });
    },

    // Check if all dependencies as specified in `command` for
    // an element are satisfied.
    verifyDependencies: function($slave, command) {
        var result=[],
            $form = $slave.closest("form"),
            $input, i, value, parts; 

        if (!$form.length) {
            $form=$(document);
        }
        for (i=0; i<command.on.length; i++) {
            parts=command.on[i];

            $input = $form.find(":input[name='"+parts[0]+"']");
            if (!$input.length) {
                result.push(false);
                continue;
            }

            if ($input.attr("type")==="radio" || $input.attr("type")==="checkbox") {
                value = $input.filter(":checked").val();
            } else {
                value = $input.val();
            }

            if ((parts.length===1 || parts[1]==="on") && !value) {
                result.push(false);
                continue;
            } else if (parts[1]==="off" && value) {
                result.push(false);
                continue;
            } else if (parts.length>2) {
                if (parts[1]==="equals" && parts[2]!==value) {
                    result.push(false);
                    continue;
                } else if (parts[1]==="notEquals" && parts[2]===value) {
                    result.push(false);
                    continue;
                }
            } 
            result.push(true);
        }

        if (command.type==="or") {
            for (i=0; i<result.length; i++) {
                if (result[i]) {
                    return true;
                }
            }
            return false;
        } else {
            for (i=0; i<result.length; i++) {
                if (!result[i]) {
                    return false;
                }
            }
            return true;
        }
    },


    // Return the list of all input elements on which the given element has
    // a declared dependency via `dependsOn` classes.
    getDependMasters: function($slave, command) {
        var $result = $(),
            $form = $slave.closest("form"),
            i, parts;

        if (!$form.length) {
            $form=$(document);
        }

        for (i=0; i<command.on.length; i++) {
            parts=command.on[i];
            if (!parts) {
                continue;
            }

            $result=$result.add($form.find(":input[name='"+parts[0]+"']"));
        }

        return $result;
    },


    // Setup dependency-tracking behaviour.
    initDepends: function(root) {
        $("*[class*='dependsOn-']", root).each(function() {
            var slave = this,
                $slave = $(this),
                $visible = $(this),
                $panel = $slave.data("mapal.infoPanel"),
                classes = $slave.attr("class").split(" "),
                command = {"on" : [],
                           "action" : "show",
                           "type": "and"
                           };
            var i, a, parts, state;

            for (i=0; i<classes.length; i++) {
                parts=classes[i].split("-");
                if (parts[0].indexOf("depends")===0) {
                    a=parts[0].substr(7).toLowerCase();
                    if (a==="on") {
                        if (parts.length>4) {
                            parts=parts.slice(0,3).concat(parts.slice(3).join("-"));
                        }
                        command.on.push(parts.slice(1));
                    } else {
                        command[a]=parts[1];
                    }
                }
            }

            state=mapal.verifyDependencies($slave, command);
            if ($panel!==undefined) {
                $visible=$visible.add($panel);
            }

            if (command.action==="show") {
                if (state) {
                    $visible.show();
                } else {
                    $visible.hide();
                }
            } else if (command.action==="enable") {
                if (state) {
                    slave.disabled=null;
                    $slave.removeClass("disabled");
                } else {
                    slave.disabled="disabled";
                    $slave.addClass("disabled");
                }
            }

            mapal.getDependMasters($slave, command).bind("change.mapal", function() {
                state=mapal.verifyDependencies($slave, command);
                if (command.action==="show") {
                    if (state) {
                        $visible.slideDown();
                    } else {
                        $visible.slideUp();
                    }
                } else if (command.action==="enable" ) {
                    if (state) {
                        slave.disabled=null;
                        $slave.removeClass("disabled");
                    } else {
                        slave.disabled="disabled";
                        $slave.addClass("disabled");
                    }
                }
            });
        });
    },


    // check if an input element has a value. 
    hasContent: function($el) {
        if ($el.is(":input")) {
            return $el.val();
        } else {
            return $el.text().replace(/\s*/g, "") || $el.find("img,object,video,audio").length;
        }
    },

    // Support for superimposing labels on input elements
    initSuperImpose: function(root) {
        $("label.superImpose", root).each(function() {
            var $label = $(this),
                forInput = $label.attr("for").replace(/([.\[\]])/g, "\\$1"),
                $myInput = forInput ? $(":input#"+forInput+", .rich[id="+forInput+"]") : $(":input", this);

            if (!$myInput.length) {
                return;
            }

            $label
                .css("display", mapal.hasContent($myInput) ? "none" : "block")
                .click(function() {
                    $myInput.focus();
                });

            setTimeout(function() {
                $label.css("display", mapal.hasContent($myInput) ? "none" : "block");
                }, 250);

            $myInput
                .bind("blur.mapal", function() {
                    $label.css("display", mapal.hasContent($myInput) ? "none" : "block");
                })
                .bind("focus.mapal", function() {
                    $label.css("display", "none");
                });
        });
    },


    // Apply some standard markup transformations
    initTransforms: function(root) {
        $(".jsOnly", root).show();

        $("legend", root).each(function() {
            var p = $('<p>'+$(this).html()+'</p>');
            $(this).replaceWith(p);

            // Copy over its attributes
            $.each($(this).get(0).attributes, function(i, a) {p.attr(a.nodeName, a.nodeValue);});
            if (p.attr('class')) {
                p.attr('class', p.attr('class') + ' legend');
            }
            else p.attr('class', 'legend');
        });
    },


    // Manage open/close/hasChild classes for a ul-based menu tree
    initMenu: function(root) {
        $("ul.menu").each(function() {
            var $menu = $(this),
                timer,
                closeMenu, openMenu,
                mouseOverHandler, mouseOutHandler;

            openMenu = function($li) {
                if (timer) {
                    clearTimeout(timer);
                    timer = null;
                }

                if (!$li.hasClass("open")) {
                    $li.siblings("li.open").each(function() { closeMenu($menu);});
                    $li.addClass("open").removeClass("closed");
                }
            };

            closeMenu = function($li) {
                $li.find("li.open").andSelf().removeClass("open").addClass("closed");
            };

            mouseOverHandler = function() {
                var $li = $(this);
                openMenu($li);
            };

            mouseOutHandler = function() {
                var $li = $(this);

                if (timer) {
                    clearTimeout(timer);
                    timer=null;
                }

                timer = setTimeout(function() { closeMenu($li); }, 1000);
            };

            $("ul.menu li", root)
                .addClass("closed")
                .filter(":has(ul)").addClass("hasChildren").end()
                .bind("mouseover.mapal", mouseOverHandler)
                .bind("mouseout.mapal", mouseOutHandler);
        });
    },

    // Utility method to facilitate AJAX content loading
    loadSnippet: function(url, selector, target, callback) {
        var $factory = $("<div/>"),
            $target = $("#"+target);

        if ($target.length===0) {
            $target = $("<div/>")
                .css("opacity", 0)
                .appendTo(document.body);
        }

        function htmlLoaded(data, textStatus, response) {
            if (response.status < 200 || response.status >= 400) {
                return;
            }

            $target.replaceWith(
                    $factory.find("#"+selector)
                        .attr("id", target)
                        .css("opacity", 0));
            $target = $("#"+target);

            mapal.initContent($target);
            callback($target);
        }

        $target.animate({opacity: 0}, "slow", function() { 
            url = url + " #" + selector;
            $factory.load(url, htmlLoaded);
        });
    },

    // Enable DOM-injection from anchors
    initDomInjection: function () {
        $("a[rel^=#]").on("click.mapal", function (e) {
            var $a = $(this),
                parts = $a.attr("href").split("#", 2),
                target = $a.attr("rel").slice(1);

            mapal.loadSnippet(parts[0], parts[1], target, function($target) {
                $target.animate({opacity: 1}, "fast");
            });

            e.preventDefault();
        });
    },

    // Event handler for forms in a panel
    panelFormHandler: function(data, status, xhr, $form) {
        // regexp taken from jQuery 1.4.1
        var rscript = /<script(.|\s)*?\/script>/gi,
            $trigger = $(this.context),
            href = this.context.tagName.toLowerCase()==="a" ? $trigger.attr("href") : $trigger.attr("name"),
            action = $form.attr("action"),
            $panel = $("#panel"),
            ct = xhr.getResponseHeader("content-type"),
            isJSON = ct.indexOf("application/json") >= 0,
            $tree, target;

        // Error or validation error
        if (isJSON || xhr.status !== 202) {
            if (isJSON) {
                var reply = $.parseJSON(xhr.responseText);
                $trigger.trigger("ajaxFormResult", reply);
                if (reply.action==="reload") {
                    location.reload();
                } else if (reply.action==="close" || !reply.action) {
                    $panel.overlay().close();
                    $panel.remove();
                }
                return;
            } else {
                $trigger.trigger("ajaxFormResult");
            }
            $panel.overlay().close();
            $panel.remove();
            return;
        }

        if (action.indexOf("#")>0) {
            target = action.split("#", 2)[1];
        } else {
            target = href.split("#", 2)[1];
        }

        $tree = $("<div/>").append(data.replace(rscript, ""));
        $tree = $tree.find("#"+target).attr("id", "panel-content");
        mapal.initContent(target);
        $("#panel-content").replaceWith($tree);
        $panel.find("form").ajaxForm({context: this.context,
                                      success: mapal.panelFormHandler});
    },

    // Load (part of a) page and open it in a modal panel
    initPanels: function() {
        $("a.openPanel[href*=#], button.openPanel[name*=#]").on("click.mapal", function (e) {
            var $trigger = $(this),
                href = this.tagName.toLowerCase()==="a" ? $trigger.attr("href") : $trigger.attr("name"),
                parts = href.split("#", 2),
                $panel = $("#panel");

            if ($panel.length===0) {
                $panel = $("<div/>")
                    .attr("id", "panel")
                    .appendTo(document.body);
                $("<div/>")
                    .attr("id", "panel-content")
                    .appendTo($panel);
            }

            mapal.loadSnippet(parts[0], parts[1], "panel-content", function($target) {
                var api;

                $target.css("opacity", 1).addClass("panel");
                $("#panel form").ajaxForm({context: $trigger.get(0),
                                           success: mapal.panelFormHandler});
                api = $panel.overlay({api: true,
                                      closeOnClick: false,
                                      expose: {color: "#333", loadSpeed: 200, opacity: 0.9}});
                api.load();
            });

            e.preventDefault();
        });
    },


    closeTooltips: function() {
        $("dfn.infoPanel.open").removeClass("open");
        $("body").unbind("click.tooltip");
    },

    initTooltip: function(root) {
        $("dfn.infoPanel:not(span)").each(function() {
            var $panel = $(this),
                title = $panel.attr("title");

            if ($panel.data("mapal.tooltip")) {
                return;
            }

            if (title) {
                $("<span/>")
                    .addClass("title")
                    .text(title)
                    .prependTo($panel);
                $panel.removeAttr("title");
            }

            $panel
                .click(function(event) {
                    if ($panel.hasClass("open")) {
                        $panel.removeClass("open");
                        $("body").unbind("click.tooltip");
                    } else {
                        mapal.closeTooltips();
                        $panel.addClass("open");
                        $("body").one("click.tooltip", mapal.closeTooltips);
                    }
                    event.stopPropagation();
                })
                .data("mapal.tooltip", true);
        });
    },

    // Utility method to update the width classes on the body
    updateWidthClasses: function() {
        var width = $(window).width(),
            $body = $("body"),
            limits;

        for (var cls in mapal.widthClasses) {
            if (mapal.widthClasses.hasOwnProperty(cls)) {
                limits=mapal.widthClasses[cls];
                if ((limits.minimum===null || limits.minimum<=width) && (limits.maximum===null || width<=limits.maximum)) {
                    $body.addClass(cls);
                } else {
                    $body.removeClass(cls);
                }
            }
        }
    },


    initWidthClasses: function() {
        mapal.updateWidthClasses();
        $(window).bind("resize.mapal", mapal.updateWidthClasses);
    },


    // No browser supports all DOM methods to get from an object to its
    // parent window and document and back again, so we convert all 
    // html objects to iframes.
    initIframes: function(root) {
        $("object[type=text/html]", root).each(function() {
            var $object = $(this),
                $iframe = $("<iframe allowtransparency='true'/>");

            $iframe
                .attr("id", $object.attr("id"))
                .attr("class", $object.attr("class"))
                .attr("src", $object.attr("data"))
                .attr("frameborder", "0")
                .attr("style", "background-color:transparent");
            $object.replaceWith($iframe);
        });
    },

    // Older IE versions need extra help to handle buttons.
    initIEButtons: function() {
        if ($.browser.msie ) {
            var version = Number( $.browser.version.split(".", 2).join(""));
            if (version>80)
                return;
        }

        $("form button[type=submit]").on("click", function() {
            var name = this.name,
                $el = $("<input/>"),
                value = this.attributes.getNamedItem("value");

            if (typeof value == "undefined") {
                return;
            }

            $el.attr("type", "hidden")
               .attr("name", name)
               .val(value.nodeValue)
               .appendTo(this.form);
            $("button[type=submit]", this.form).attr("name", "_buttonfix");
        });

    },

    // Setup a DOM tree.
    initContent: function(root) {
        mapal.initTransforms(root);
        mapal.initAutofocus(root);
        mapal.initAutocomplete(root);
        mapal.initDepends(root);
        mapal.initSuperImpose(root);
        mapal.initTooltip(root);
        mapal.initMenu(root);
        // Replace objects with iframes for IE 8 and older.
        if ($.browser.msie ) {
            var version = Number( $.browser.version.split(".", 2).join(""));
            if (version<=90) {
                mapal.initIframes(root);
            }
        }

        $(root).trigger("newContent", root);
    },


    // Setup global behaviour
    init: function() {
        mapal.initWidthClasses();
        mapal.initDomInjection();
        mapal.initPanels();
        mapal.initIEButtons();
    }
};


$(document).ready(function() {
    mapal.registerWidthClass("narrow", 0, 780);
    mapal.registerWidthClass("medium", 0, 1109);
    mapal.registerWidthClass("wide", 1110, null);
    mapal.init();
    mapal.initContent(document.body);
    $(document).trigger("setupFinished", document);
});

});
