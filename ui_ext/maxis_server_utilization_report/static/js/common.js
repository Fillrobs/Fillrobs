export class LoaderClass {
  constructor(tagName) {
    this.tagName = tagName;
  }

  display() {
    $(`${this.tagName} .loader`).addClass('in');
    $(`${this.tagName} .loader.fade.in`).css({
      "width": `${$(`#${this.tagName}`).parent().width()}px`,
      "bottom": 'none',
      "left": `${$(`#${this.tagName}`).parent().position().left}px`,
      "right": 'none',
    });
  }

  hide() { $(`${this.tagName} .loader`).removeClass('in'); }

}