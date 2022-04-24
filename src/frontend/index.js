// const BACKEND_URL = "https://api.reader.henrydashwood.com";
const BACKEND_URL = "https://localhost:8000";
const ul = document.getElementById("feeds_list");

const getData = async () => {
  const resp = await fetch(`${BACKEND_URL}/articles`);
  console.log("here");
  const json = await resp.json();
  console.log(json);
  return json;
};

const getLatestUpdateTimestamp = async () => {
  const resp = await fetch(`${BACKEND_URL}/updates/latest`);
  const json = await resp.json();
  return json;
};

const updateArticle = async (id, body) => {
  const resp = await fetch(`${BACKEND_URL}/articles/read/${id}`, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
    method: "PATCH",
    body: JSON.stringify(body),
  });
  const json = await resp.json();
  return json;
};

const toggleReadCheckbox = async (e) => {
  if (e.target.checked) e.target.parentNode.read = true;
  else e.target.parentNode.read = false;
  id = e.target.parentNode.id;
  body = {
    title: e.target.parentNode.querySelector(".link").innerText,
    url: e.target.parentNode.querySelector(".link").href,
    source: e.target.parentNode.querySelector(".source").innerText,
    published_date:
      e.target.parentNode.querySelector(".published_date").innerText,
    read: e.target.parentNode.read,
  };
  json = updateArticle(id, body);
};

const clickLink = async (e) => {
  e.target.parentNode.querySelector(".readFlag").checked = true;
  id = e.target.parentNode.id;
  body = {
    title: e.target.parentNode.querySelector(".link").innerText,
    url: e.target.parentNode.querySelector(".link").href,
    source: e.target.parentNode.querySelector(".source").innerText,
    published_date:
      e.target.parentNode.querySelector(".published_date").innerText,
    read: true,
  };
  json = updateArticle(id, body);
};

const createArticleRow = (dataElement) => {
  const row = document.createElement("div");
  row.classList.add("row");
  row.setAttribute("id", dataElement.id);

  const readFlag = document.createElement("INPUT");
  readFlag.classList.add("readFlag");
  readFlag.setAttribute("type", "checkbox");
  if (dataElement.read) readFlag.checked = true;
  readFlag.addEventListener("change", toggleReadCheckbox);
  row.appendChild(readFlag);

  const source = document.createElement("p");
  source.appendChild(document.createTextNode(dataElement.source));
  source.classList.add("source");
  row.appendChild(source);

  const a = document.createElement("a");
  a.classList.add("link");
  a.appendChild(document.createTextNode(dataElement.title));
  a.href = dataElement.url;
  a.setAttribute("target", "_blank");
  a.addEventListener("click", clickLink);
  row.appendChild(a);

  const publishedDate = document.createElement("p");
  publishedDate.appendChild(
    document.createTextNode(dataElement.published_date)
  );
  publishedDate.classList.add("published_date");
  row.appendChild(publishedDate);

  return row;
};

const displayData = async () => {
  const articles = await getData();
  const latestUpdate = await getLatestUpdateTimestamp();
  articles.forEach((dataElement) => {
    const li = document.createElement("li");
    row = createArticleRow(dataElement);
    li.appendChild(row);
    ul.appendChild(li);
  });
  const last_update = document.getElementById("last_update");
  last_update.innerText = `Last updated: ${latestUpdate}`;
};

displayData();
