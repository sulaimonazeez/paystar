

function Payvassel() {
  let payvassel = document.getElementById("payvessel");
  let monnify = document.getElementById("monnify");
  payvessel.style.display = "block";
  monnify.style.display = "none";
}

function Monnify() {
  let payvassel = document.getElementById("payvessel");
  let monnify = document.getElementById("monnify");
  payvessel.style.display = "none";
  monnify.style.display = "block";
}

function Redirect(data) {
  x = document.createElement("a");
  x.setAttribute("href", data);
  x.click();
  console.log("redirecting...")
  alert("moving")
}

$(document).ready(() =>{
  let airtelPlan = new Map([
            ["Airtel Corporation 1GB", 285],
            ["Airtel Corporation 2GB", 570],
            ["Airtel Corporation 3GB", 840]
        ]);

  let mtnPlan = new Map([
            ["MTN SME 1GB", 285],
            ["MTN SME 2GB", 570],
            ["MTN SME 3GB", 840]
        ]);

  let gloPlan = new Map([
            ["Glo Corporation 1GB", 285],
            ["Glo Corporation 2GB", 570],
            ["Glo Corporation 3GB", 840]
        ]);

        // Function to populate the .sme-cop dropdown
  function trickLayer(data) {
    let $myList = $(".data-amounts");
    // Empty the list if there's existing data
    $myList.empty();
    // Add a default option
    $myList.append('<option value="" selected disabled>Select Plan</option>');
    for (const [dataAmount, amountToPay] of data) {
      $myList.append(`<option value="${dataAmount}">${dataAmount}</option>`);
    }
  }

  // Event handler for the .selecting dropdown
  $(".selecting").change(function() {
    let $isChange = $(this).val();
    if ($isChange === "Airtel") {
      trickLayer(airtelPlan);
    } else if ($isChange === "MTN") {
      trickLayer(mtnPlan);
    } else if ($isChange === "Glo") {
      trickLayer(gloPlan);
    }
    // Clear the amount field when changing network
    $('#fixed-price').val('');
        });
    // Event handler for the .sme-cop dropdown
    $(".data-amounts").change(function() {
      let selectedPlan = $(this).val();
      let selectedNetwork = $(".selecting").val();
      let amount = null;
      if (selectedNetwork === "Airtel") {
        amount = airtelPlan.get(selectedPlan);
      } else if (selectedNetwork === "MTN"){
        amount = mtnPlan.get(selectedPlan);
      }else if (selectedNetwork === "Glo"){
        amount = gloPlan.get(selectedPlan);
        
      }
      // Display the amount in the input field
      if (amount !== null) {
        $('#fixed-price').val('₦' + amount);
      }else {
        $('#fixed-price').val('');
      }
  });
  let toGo = document.createElement("a");
  $("#data").click(() =>{
    toGo.setAttribute("href", "/databundle");
    toGo.click();
  });
  $("#upgrade").click(() =>{
    toGo.setAttribute("href", "/upgrade");
    toGo.click();
  });
  $("#myprofile").click(() =>{
    toGo.setAttribute("href", "/profile");
    toGo.click();
  });
  $("#more").click(() =>{
    toGo.setAttribute("href", "/more");
    toGo.click();
  });
});
