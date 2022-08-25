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
        formData.append("username", this.form.elements["username_login"].value);
        formData.append("password", this.form.elements["password_login"].value);
        console.log(process.env.BACKEND_URL);
        fetch(`${process.env.BACKEND_URL}/users/token`, {
          method: "post",
          body: formData,
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.hasOwnProperty("access_token")) {
              localStorage.setItem("token", `Bearer ${data["access_token"]}`);
              localStorage.setItem("auth", 1);
              window.location.replace("feed.html");
            } else {
              document.querySelector(".error-message-all").style.display =
                "block";
              document.querySelector(".error-message-all").innerText =
                "Incorrect username or password";
            }
          });
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
        const min_length = 6;
        if (field.value.length < min_length) {
          this.setStatus(
            field,
            `${field.previousElementSibling.innerText} must be at least ${min_length} characters`,
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

const loginForm = document.querySelector("#loginForm");
if (loginForm) {
  const fields = ["username_login", "password_login"];
  const validator = new Login(loginForm, fields);
}

const registerAccount = async (e) => {
  e.preventDefault();
  resp = await fetch(`${process.env.BACKEND_URL}/users/register`, {
    method: "post",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      username: createAccountForm.elements["username_create"].value,
      password: createAccountForm.elements["password_create"].value,
    }),
  });
};

const createAccountForm = document.querySelector("#createAccountForm");
createAccountForm.addEventListener("submit", registerAccount);
