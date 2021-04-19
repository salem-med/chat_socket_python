
msgs = [{"nom" : "salem", "msg" : "how are you", "date_heure" : "auj", "lst_tag" : ["salem", "khalid"]}, {"nom" : "salem", "msg" : "how are you", "date_heure" : "auj", "lst_tag" : ["salem", "khalid"]}]
def save_in_xml():
    from lxml import etree
    messages = etree.Element("messages")

    for msg in msgs:
        message = etree.SubElement(messages, "message")
        utilisateur = etree.SubElement(message, "utilisateur")
        utilisateur.text = msg["nom"]
        date_heure = etree.SubElement(message, "date_heure")
        date_heure.text = msg["date_heure"]
        text_msg = etree.SubElement(message, "text")
        text_msg.text = msg["msg"]
        print(msg["lst_tag"])
        for tag in msg["lst_tag"]:
            tagE = etree.SubElement(message, "tag")
            tagE.text = tag


    from xml.dom import minidom

    a_enregistrer = minidom.parseString(etree.tostring(messages)).toprettyxml(indent="   ")
    with open("./server-log.xml", "w") as f:
        f.write(a_enregistrer)

save_in_xml()