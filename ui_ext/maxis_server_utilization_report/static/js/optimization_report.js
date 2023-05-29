import { LoaderClass } from './common.js';
import { createHeader, createFooter } from './pdf_common.js';

// var loaderObjServer = new LoaderClass('chart-group');

var pageGap = 0;

function downloadPDF() {
  var doc = new jsPDF();

  pageGap = 10;
  doc.setFont('helvetica');
  doc.setFontType('bold');
  createHeader(doc);
  doc.setFontSize(12);
  doc.text(pageGap, pageGap + 25, 'OpenStack Optimization Report:');
  doc.autoTable({ html: '#optimization-report', startY: 40, margin: { right: 10, left: 10 }, pageBreak: 'auto' });

  let report_name = "OpenStack Optimization Report".split(' ').join('_') + moment().format('_DDMMYYYYhhmmss');
  createFooter(doc);
  doc.save(report_name + '.pdf');
}

$(document).ready(function () {
  //   loaderObjServer.display();
  $('#optimization-report').DataTable();
  //   loaderObjServer.hide();
  $(document).on('click', '#pdf-report', function (e) {
    downloadPDF();
  });
});