# -*- coding: utf-8 -*-
__title__ = 'Import Linked Sheets'
__author__ = 'David Versteeg, with help from OpenAI ChatGPT'
__context__ = 'sheet'

from Autodesk.Revit.DB import (
    FilteredElementCollector,
    ViewSheet,
    RevitLinkInstance,
    ExternalDefinitionCreationOptions,
    ParameterElement,
    BuiltInParameterGroup,
    BuiltInCategory,
    Transaction,
    SpecTypeId
)
from pyrevit import revit, DB, script

output = script.get_output()
doc = revit.doc

# Configurable
TRACKING_PARAM = "LinkedSheetGUID"

def get_linked_docs_and_instances(doc):
    linked = []
    collector = FilteredElementCollector(doc).OfClass(RevitLinkInstance)
    for inst in collector:
        link_doc = inst.GetLinkDocument()
        if link_doc:
            linked.append((inst, link_doc))
    return linked

def get_indexed_sheets(link_doc):
    sheets = []
    for s in FilteredElementCollector(link_doc).OfClass(ViewSheet):
        include_param = s.LookupParameter("Appears In Sheet List")
        if include_param and include_param.AsInteger() == 1:
            sheets.append(s)
    return sheets

def get_existing_placeholder_sheets(doc):
    sheets = {}
    for s in FilteredElementCollector(doc).OfClass(ViewSheet):
        if s.IsPlaceholder:
            guid_param = s.LookupParameter(TRACKING_PARAM)
            if guid_param and guid_param.AsString():
                sheets[guid_param.AsString()] = s
    return sheets

def generate_guid(link_instance, sheet):
    return "{}_{}".format(link_instance.UniqueId, sheet.Id.IntegerValue)

def ensure_project_parameter(doc):
    bindings = doc.ParameterBindings
    found = False

    it = bindings.ForwardIterator()
    it.Reset()
    while it.MoveNext():
        if it.Key.Name == TRACKING_PARAM:
            found = True
            break

    if not found:
        output.print_md("**Missing required project parameter:** `{}`".format(TRACKING_PARAM))
        output.print_md("Please create a **project parameter** named `{}` (Text type) applied to Sheets. Feel free to ask for help if you do not know how to do this ;)".format(TRACKING_PARAM))
        # raise Exception("Required project parameter not found.")
        script.exit()

def update_or_create_sheet(doc, name, number, guid, existing_sheets):
    if guid in existing_sheets:
        sheet = existing_sheets[guid]
        sheet.Name = name
        sheet.SheetNumber = number
        return "updated", sheet
    else:
        new_sheet = ViewSheet.CreatePlaceholder(doc)
        new_sheet.Name = name
        new_sheet.SheetNumber = number
        param = new_sheet.LookupParameter(TRACKING_PARAM)
        if param:
            param.Set(guid)
        return "created", new_sheet

# Main Execution

ensure_project_parameter(doc)
existing_sheets = get_existing_placeholder_sheets(doc)

created = 0
updated = 0

t = Transaction(doc, "Sync Linked Sheets")
t.Start()

for link_inst, link_doc in get_linked_docs_and_instances(doc):
    for sheet in get_indexed_sheets(link_doc):
        guid = generate_guid(link_inst, sheet)
        status, _ = update_or_create_sheet(doc, sheet.Name, sheet.SheetNumber, guid, existing_sheets)
        if status == "created":
            created += 1
        elif status == "updated":
            updated += 1

t.Commit()

output.print_md("**Placeholder Sheets Updated:** {}  \n**Placeholder Sheets Created:** {}".format(updated, created))