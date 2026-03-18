---
title: Home
layout: home
nav_order: 1
---

दुतावास (Dutawas) bridges the information gap for Nepali citizens by providing clear, accessible documentation about services offered by the Embassy of Nepal in the United States.

{: .warning }
This is an independent, community-maintained resource and is not affiliated with the Government of Nepal or its diplomatic missions.

## Nepali Consulates in the United States

| Location | Phone | Consular Hours | Serves |
|---|---|---|---|
| [New York](/consulates/new-york/) | +1 (917) 675-6783 | Mon–Fri 9:30 AM–2:30 PM | NY, NJ, CT, PA, MA, RI, VT, NH, ME |
| [Dallas](/consulates/dallas/) | +1 (972) 803-5394 | Mon–Fri 10:00 AM–12:30 PM | Being finalized — contact consulate |
| [Washington State](/consulates/washington-state/) | +1 (206) 324-9000 | Call for hours | WA and region |
| [Boston](/consulates/boston/) | — | — | Served by New York consulate |

## Which Consulate Serves My State?

<div style="margin: 1rem 0;">
  <select id="stateSelect" style="padding: 10px; font-size: 1rem; width: 100%; max-width: 400px; border: 1px solid #ccc; border-radius: 4px;">
    <option value="">-- Select your state --</option>
    <option value="AL">Alabama</option>
    <option value="AK">Alaska</option>
    <option value="AZ">Arizona</option>
    <option value="AR">Arkansas</option>
    <option value="CA">California</option>
    <option value="CO">Colorado</option>
    <option value="CT">Connecticut</option>
    <option value="DE">Delaware</option>
    <option value="DC">District of Columbia</option>
    <option value="FL">Florida</option>
    <option value="GA">Georgia</option>
    <option value="HI">Hawaii</option>
    <option value="ID">Idaho</option>
    <option value="IL">Illinois</option>
    <option value="IN">Indiana</option>
    <option value="IA">Iowa</option>
    <option value="KS">Kansas</option>
    <option value="KY">Kentucky</option>
    <option value="LA">Louisiana</option>
    <option value="ME">Maine</option>
    <option value="MD">Maryland</option>
    <option value="MA">Massachusetts</option>
    <option value="MI">Michigan</option>
    <option value="MN">Minnesota</option>
    <option value="MS">Mississippi</option>
    <option value="MO">Missouri</option>
    <option value="MT">Montana</option>
    <option value="NE">Nebraska</option>
    <option value="NV">Nevada</option>
    <option value="NH">New Hampshire</option>
    <option value="NJ">New Jersey</option>
    <option value="NM">New Mexico</option>
    <option value="NY">New York</option>
    <option value="NC">North Carolina</option>
    <option value="ND">North Dakota</option>
    <option value="OH">Ohio</option>
    <option value="OK">Oklahoma</option>
    <option value="OR">Oregon</option>
    <option value="PA">Pennsylvania</option>
    <option value="RI">Rhode Island</option>
    <option value="SC">South Carolina</option>
    <option value="SD">South Dakota</option>
    <option value="TN">Tennessee</option>
    <option value="TX">Texas</option>
    <option value="UT">Utah</option>
    <option value="VT">Vermont</option>
    <option value="VA">Virginia</option>
    <option value="WA">Washington</option>
    <option value="WV">West Virginia</option>
    <option value="WI">Wisconsin</option>
    <option value="WY">Wyoming</option>
  </select>
</div>

<div id="consulate-result" style="margin-top: 1rem; padding: 1rem; border-left: 4px solid #e63329; background: #fef2f2; display: none;">
</div>

{% raw %}
<script>
(function() {
  var ny = {
    name: "Consulate General of Nepal, New York",
    phone: "+1 (917) 675-6783",
    email: "cgnnewyork@mofa.gov.np",
    url: "/consulates/new-york/"
  };
  var dallas = {
    name: "Consulate General of Nepal, Dallas",
    phone: "+1 (972) 803-5394",
    email: "info@nepalconsulatedallas.org",
    url: "/consulates/dallas/"
  };
  var wa = {
    name: "Nepal Consulate, Washington State",
    phone: "+1 (206) 324-9000",
    email: "nepalconsulate@gmail.com",
    url: "/consulates/washington-state/",
    note: "This is an honorary consulate with limited services. For e-passport and major consular services, contact the Embassy in Washington DC."
  };
  var dc = {
    name: "Embassy of Nepal, Washington DC",
    phone: "+1 (202) 774-4780",
    email: "info@nepalembassyusa.org",
    url: "https://us.nepalembassy.gov.np"
  };

  var mapping = {
    CT: ny, ME: ny, MA: ny, NH: ny, NJ: ny, NY: ny, PA: ny, RI: ny, VT: ny,
    TX: dallas,
    WA: wa,
    AL: dc, AK: dc, AZ: dc, AR: dc, CA: dc, CO: dc, DE: dc, DC: dc,
    FL: dc, GA: dc, HI: dc, ID: dc, IL: dc, IN: dc, IA: dc, KS: dc,
    KY: dc, LA: dc, MD: dc, MI: dc, MN: dc, MS: dc, MO: dc, MT: dc,
    NE: dc, NV: dc, NM: dc, NC: dc, ND: dc, OH: dc, OK: dc, OR: dc,
    SC: dc, SD: dc, TN: dc, UT: dc, VA: dc, WV: dc, WI: dc, WY: dc
  };

  var select = document.getElementById("stateSelect");
  var result = document.getElementById("consulate-result");

  select.addEventListener("change", function() {
    var state = select.value;
    var c = mapping[state];
    if (c) {
      var html = "<strong>" + c.name + "</strong><br>" +
        "Phone: " + c.phone + "<br>" +
        "Email: <a href='mailto:" + c.email + "'>" + c.email + "</a><br>" +
        "<a href='" + c.url + "'>View full details &rarr;</a>";
      if (c.note) {
        html += "<br><br><em>" + c.note + "</em>";
      }
      result.style.display = "block";
      result.innerHTML = html;
    } else {
      result.style.display = "none";
    }
  });
})();
</script>
{% endraw %}

## Emergency Contacts

| Office | Phone | For |
|---|---|---|
| Embassy of Nepal, Washington DC | +1 (202) 774-4780 | All US residents |
| Consulate General, New York | +1 (917) 675-6783 | Eastern states |
| Consulate General, Dallas | +1 (972) 803-5394 | Southern states |
| Nepal Police Emergency | 100 | Emergencies in Nepal |
| Ministry of Foreign Affairs | +977-1-4200163 | Nepal government |
| MoFA Toll Free (from Nepal) | 1660-01-00186 | Nepal government |
