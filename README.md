# pyRevit-LinkedModelSheetImporter
Extension to pyRevit Core's UI adding a utility to automatically import and update sheets from linked model as placeholder sheets in the main model.

The script will check every linked model for sheets that are set to be included in the sheet index and pull it into the host model as a placeholder sheet. It will attach a unique identifier to the placeholder sheet so the next time the script is executed it will update the sheet name and sheet number rather than creating a new placeholder sheet.



!important

Script requires project to be set up with a project parameter named "LinkedSheetGUID". Due to changes to the Revit API between Revit years, having the script create this result in a much more fragile code that then becomes harder to fix if it does break.
