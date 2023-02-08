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
          document.querySelector('input[id="fullName"]').value = '';
          document.querySelector('input[id="value"]').value = '';
          refreshLabels();
          alertOVRL('Label created','success');
        },
        error: function(xhr, status, error) {
          alertOVRL(xhr.statusText,'error');
        }
      });
    }
  }
}

function init() {
  refreshLabels();
}

labels = []

function refreshLabels() {
  document.querySelector("#refreshLabels")?.setAttribute('disabled','');
  $.ajax({
    url: '/getLabels',
    type: "POST",
    success: function (xhr,status,state) {
      document.querySelector("#refreshLabels")?.removeAttribute('disabled');
      if(state.status==200){
        labels = xhr;
        updateSearchResults();
      }
    },
    error: function(xhr, status, error) {
      document.querySelector("#refreshLabels")?.removeAttribute('disabled');
      alertOVRL(xhr.statusText,'error');
    }
  });
}

results = []
function updateSearchResults () {
  const query = document.querySelector('#searchInput')?.value;
  let re;
  if(query && query.length>=2) {
    re = new RegExp(query,'i');
    results = labels.filter((l)=>{
      return re.test(l.fullName) ||
        re.test(l.categories) ||
        re.test(l.value) ||
        re.test(l.shortDescription)
    })
  } else {
    results = []
  }
  const row = document.querySelector("#rowPrototype");
  const tableContent = document.querySelector('#tableContent');
  if(!row || !tableContent) return;
  tableContent.innerHTML = '';
  results.forEach( r => {
    const newRow = row.cloneNode(true);
    newRow.removeAttribute("id");
    Object.keys(r).forEach(key => {
      const field = newRow.querySelector('#'+key);
      if (field) {
        field.innerHTML = r[key].toString().replace(re,'<focus>$&</focus>'); 
      }
    });
    tableContent.appendChild(newRow);
  });
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