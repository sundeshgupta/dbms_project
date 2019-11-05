$('textarea').each(function () {
  this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
}).on('input', function () {
  this.style.height = 'auto';
  this.style.height = (this.scrollHeight) + 'px';
});

$('textarea').each(function () {
  this.setAttribute('style', 'width:' + (this.scrollWidth) + 'px;overflow-y:hidden;');
}).on('input', function () {
  this.style.width = 'auto';
  this.style.width = (this.scrollWidth) + 'px';
});
