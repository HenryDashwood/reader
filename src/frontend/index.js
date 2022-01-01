const BACKEND_URL = "http://api.reader.henrydashwood.com/";
// const BACKEND_URL = "http://localhost:8000/";
const ul = document.getElementById("feeds_list");

const getData = async () => {
  const resp = await fetch(BACKEND_URL);
  const json = await resp.json();
  return json;
};

const displayData = async () => {
  const json = await getData();
  json["data"].forEach((element) => {
    const li = document.createElement("li");
    const row = document.createElement("div");
    row.classList.add("row");
    const source = document.createElement("p");
    source.appendChild(document.createTextNode(element.source));
    row.appendChild(source);
    const a = document.createElement("a");
    a.appendChild(document.createTextNode(element.title));
    a.href = element.link;
    a.setAttribute("target", "_blank");
    row.appendChild(a);
    li.appendChild(row);
    ul.appendChild(li);
  });
  const last_update = document.getElementById("last_update");
  last_update.innerText = `Last updated: ${json["last_update"]}`;
};

displayData();
