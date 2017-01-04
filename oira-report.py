"""Plucks out the most important details from the Robot reports for
OiRA

This parses the robot output.xml and produces an HTML file called
oira-report.html
"""

from lxml import etree
from lxml import html
from lxml.html import builder as E


# A plain template with Bootstrap
report = E.HTML(
    E.HEAD(
        E.LINK(
            href=("http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/css/"
                  "bootstrap-combined.min.css"),
            rel="stylesheet",
        ),
        E.TITLE("OiRA Testing Report"),
        E.META(name="viewport", content="width=device-width, initial-scale=1.0")
    ),
    E.BODY(
        E.DIV(
            E.CLASS("container"),
            E.DIV(
                E.CLASS("page-header"),
                E.H1("OiRA Testing Report",)
            ) ,
            id="content-area",
        ),
    ),
)

def format_msg(msg, status):
    if msg.text is not None:
        if "password" in msg.text:
            """Strip out the test password, just in case the report gets sent
            around."""
            return E.P("Entering password")
        if status == "FAIL":
            msg_html = html.fromstring(msg.text)
            if msg_html.xpath(".//a") != []:
                href = msg_html.xpath(".//a")[0].get("href")
                return E.UL(
                    E.CLASS("thumbnails"),
                    E.LI(
                        E.CLASS("span4"),
                        E.A(E.CLASS("thumbnail"),
                            E.IMG(src=href),
                            href=href,
                        ),
                    )
                )
            else:
                return E.P(msg.text)
        else:
            return E.P(msg.text)

content_area = report.get_element_by_id("content-area")
def process_robot_output(robot_output):
    root = etree.parse(robot_output).getroot()
    print "one time"
    for suite in root.xpath("//suite[@source]"):
        suite_id = suite.get("id", "")
        suite_container = E.DIV(E.CLASS("suite span12"), id=suite_id)
        suite_container.append(E.H3(E.CLASS("span12"), suite.get("name", "")))

        tests = suite.xpath(".//test")
        for i, test in enumerate(tests):
            test_id = "{0}".format(test.get("id", ""))

            test_container = E.DIV(E.CLASS("span6"))
            test_name = test.get("name", "")

            test_container.append(E.H4(test_name),)

            doc = "".join([
                doc.text for doc in test.xpath("./doc")
                if doc.text is not None
            ])
            test_container.append(E.P(doc))

            status_tags = test.xpath("./status")
            status = ""
            if status_tags != []:
                status = status_tags[0].get("status")
                if status == "PASS":
                    btn_class = "btn-success"
                    text_class = "text-success"
                elif status == "FAIL":
                    btn_class = "btn-danger"
                    text_class = "text-error"

            btn_id = test_id+"-btn"
            test_container.append(
                E.BUTTON(
                    status,
                    E.CLASS("btn "+btn_class),
                    type="button",
                    id=btn_id,
                )
            )

            btn = test_container.get_element_by_id(btn_id)
            btn.set("data-target", "#"+test_id)
            btn.set("data-toggle", "collapse")


            messages = E.DIV(
                E.CLASS("collapse "+ text_class),
                id = test_id,
            )
            for kw in test.xpath("./kw"):
                for msg in kw.xpath(".//msg"):
                    messages.append(format_msg(msg, status=status))
                if kw.get("name") == \
                   "Selenium2Library.Wait Until Page Contains":
                    text_check = [
                        "text" in doc.text for doc in kw.xpath(".//doc")]
                    if text_check:
                        text_match = " ".join(
                            [arg.text for arg in kw.xpath(".//arg")])
                    messages.append(
                        E.P("Checking the page contains: "+text_match))
            test_container.append(messages)

            # Two columns per row
            if i % 2 == 0 or i == len(tests):
                row = E.DIV(
                    E.CLASS("row"),
                    test_container,
                )
                suite_container.append(row)
            else:
                row.append(test_container)

        content_area.append(E.DIV(E.CLASS("row"), suite_container))

    # ScrollSpy might be nice
    # report.body.set("data-spy","scroll")
    # report.body.set("data-target", ".suite")
    report.append(
        E.SCRIPT(
            src="http://code.jquery.com/jquery-1.9.1.min.js"
        ))

    report.append(
        E.SCRIPT(
            src="http://netdna.bootstrapcdn.com/twitter-bootstrap/2.3.2/js/bootstrap.min.js"
        ))

if __name__ == "__main__":
    robot_output = open("output.xml", "r")
    process_robot_output(robot_output)

    report_output = open("oira-report.html", "w")
    report_output.write(html.tostring(report))
