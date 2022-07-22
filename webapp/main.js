function submit() {
  const form = document.querySelector('.needs-validation');
  if (form) {
    const groups = Array.from(form.querySelectorAll('.form-group'));
    let allValid = true
    newLabel = {}
    groups.forEach((g) => {
      const input = g.querySelector('input');
      newLabel[input.id] = input.value;
      if(input.checkValidity()) {
        g.classList.add('is-valid');
        g.classList.remove('is-invalid');
      } else {
        allValid = false;
        g.classList.add('is-invalid');
        g.classList.remove('is-valid');
      }
    });

    if(allValid) {
      console.log(newLabel);
      $.ajax({
        url: '/newLabel',
        type: "POST",
        data: JSON.stringify(newLabel),
        contentType: 'application/json; charset=utf-8',
        success: function () {
          document.querySelector('input[id="fullName"]').value = ''
          document.querySelector('input[id="value"]').value = ''
          alertOVRL('Label created','success');
        },
        error: function(xhr, status, error) {
          alertOVRL(xhr.statusText,'error');
        }
    });
    }
  }
}

let alertTimeout = null

function alertOVRL(text,theme) {
  const elem = document.querySelector('#alertOverlay');
  elem.innerHTML = text;
  elem.setAttribute('theme',theme);
  elem.classList.add('show');
  if(alertTimeout) {
    window.clearTimeout(alertTimeout);
  }
  alertTimeout = setTimeout(() => {
    const elem = document.querySelector('#alertOverlay');
    elem.classList.remove('show');
    alertTimeout=null
  },5000);
}