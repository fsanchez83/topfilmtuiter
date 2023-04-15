/**
 * Auto-populate Question options in Google Forms
 * from values in Google Spreadsheet
 *
 * Written by Amit Agarwal (MIT License)
 *
 **/

const populateGoogleForms = () => {
  const GOOGLE_SHEET_NAME = 'TFT1919';
  const GOOGLE_FORM_ID = 'PONER ID DEL FORMULARIO';

  const ss = SpreadsheetApp.getActiveSpreadsheet();

  const [header, ...data] = ss.getSheetByName(GOOGLE_SHEET_NAME).getDataRange().getDisplayValues();

  const choices = {};
  header.forEach((title, i) => {
    choices[title] = data.map((d) => d[i]).filter((e) => e);
  });

  FormApp.openById(GOOGLE_FORM_ID)
    .getItems()
    .map((item) => ({
      item,
      values: choices[item.getTitle()],
    }))
    .filter(({ values }) => values)
    .forEach(({ item, values }) => {
      switch (item.getType()) {
        case FormApp.ItemType.CHECKBOX:
          item.asCheckboxItem().setChoiceValues(values);
          break;
        case FormApp.ItemType.LIST:
          item.asListItem().setChoiceValues(values);
          break;
        case FormApp.ItemType.MULTIPLE_CHOICE:
          item.asMultipleChoiceItem().setChoiceValues(values);
          break;
        default:
        // ignore item
      }
    });
  ss.toast('Google Form Updated !!');
};