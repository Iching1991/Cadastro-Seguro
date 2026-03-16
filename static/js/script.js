// =============================
// Cadastro Seguro - Script JS
// =============================


// confirmação de ações administrativas
document.addEventListener("DOMContentLoaded", function () {

    const approveButtons = document.querySelectorAll(".approve");
    const deleteButtons = document.querySelectorAll(".delete");


    approveButtons.forEach(btn => {

        btn.addEventListener("click", function (e) {

            const confirmacao = confirm("Deseja realmente aprovar este usuário?");

            if (!confirmacao) {
                e.preventDefault();
            }

        });

    });


    deleteButtons.forEach(btn => {

        btn.addEventListener("click", function (e) {

            const confirmacao = confirm("Tem certeza que deseja excluir este registro?");

            if (!confirmacao) {
                e.preventDefault();
            }

        });

    });

});



// =============================
// Validação simples de cadastro
// =============================

const cadastroForm = document.querySelector("form[action='/cadastro']");

if (cadastroForm) {

    cadastroForm.addEventListener("submit", function (e) {

        const senha = document.querySelector("input[name='senha']").value;

        if (senha.length < 6) {

            alert("A senha deve ter pelo menos 6 caracteres");

            e.preventDefault();

        }

    });

}



// =============================
// alerta visual para mensagens
// =============================

function mostrarMensagem(msg) {

    const box = document.createElement("div");

    box.innerText = msg;

    box.style.position = "fixed";
    box.style.top = "20px";
    box.style.right = "20px";
    box.style.background = "#16a34a";
    box.style.color = "white";
    box.style.padding = "10px 20px";
    box.style.borderRadius = "6px";
    box.style.boxShadow = "0 2px 10px rgba(0,0,0,0.2)";

    document.body.appendChild(box);

    setTimeout(() => {

        box.remove();

    }, 3000);

}



// =============================
// melhoria UX para tabelas
// =============================

const rows = document.querySelectorAll("table tr");

rows.forEach(row => {

    row.addEventListener("mouseover", function () {

        this.style.background = "#f3f4f6";

    });

    row.addEventListener("mouseout", function () {

        this.style.background = "white";

    });

});
