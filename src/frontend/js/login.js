// const BACKEND_URL = "https://api.reader.henrydashwood.com";
const BACKEND_URL = "https://localhost:8000";

class Login {
  constructor(form, fields) {
    this.form = form;
    this.fields = fields;
    this.validateonSubmit();
  }

  validateonSubmit() {
    this.form.addEventListener("submit", (e) => {
      e.preventDefault();
      var error = 0;
      this.fields.forEach((field) => {
        const input = document.querySelector(`#${field}`);
        if (this.validateFields(input) == false) {
          error++;
        }
      });
      if (error == 0) {
        const formData = new FormData();
        formData.append("username", document.querySelector("#username").value);
        formData.append("password", document.querySelector("#password").value);
        fetch(`${BACKEND_URL}/token`, {
          method: "post",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.error) {
              console.error("Error:", data.message);
              document.querySelector(".error-message-all").style.display =
                "block";
              document.querySelector(".error-message-all").innerText =
                "Incorrect username or password";
            } else {
              console.log(data);
              fetch(`${BACKEND_URL}/users/me/items`, {
                method: "GET",
                headers: {
                  accept: "application/json",
                  Authorization: "Bearer " + data["access_token"],
                },
              })
                .then((response) => response.json())
                .then((data) => {
                  console.log(data);
                  localStorage.setItem("user", JSON.stringify(data));
                  localStorage.setItem("auth", 1);
                  this.form.submit();
                });
            }
          })
          .catch((data) => console.error("Error:", data.message));
      }
    });
  }

  validateFields(field) {
    if (field.value.trim() === "") {
      this.setStatus(
        field,
        `${field.previousElementSibling.innerText} cannot be blank`,
        "error"
      );
      return false;
    } else {
      if (field.type == "password") {
        if (field.value.length < 6) {
          this.setStatus(
            field,
            `${field.previousElementSibling.innerText} must be at least 8 characters`,
            "error"
          );
          return false;
        } else {
          this.setStatus(field, null, "success");
          return true;
        }
      } else {
        this.setStatus(field, null, "success");
        return true;
      }
    }
  }

  setStatus(field, message, status) {
    const errorMessage = field.parentElement.querySelector(".error-message");

    if (status == "success") {
      if (errorMessage) {
        errorMessage.innerText = "";
      }
      field.classList.remove("input-error");
    }

    if (status == "error") {
      errorMessage.innerText = message;
      field.classList.add("input-error");
    }
  }
}

const form = document.querySelector("#loginForm");
if (form) {
  const fields = ["username", "password"];
  const validator = new Login(form, fields);
}
