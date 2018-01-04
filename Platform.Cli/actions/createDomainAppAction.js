module.exports = class CreateDomainAppAction{
    
    /** 
     * @method create
     * @description Monta a estrutura básica de uma aplicação de dominio
     * */ 
    create(){
        var shell = require('shelljs');
        
        var inquirer = require('inquirer');
        var fs = require("fs");
        
        var plataforma = {};
        plataforma.app = {};
        
        inquirer.prompt(this.getQuestions()).then(answers => {
            var name = answers["nome"];
            var path = process.cwd()+"/"+name;
            plataforma.app.name = name;
            shell.mkdir('-p', path+'/Dominio',path+'/Migrations');
            
            plataforma.app.version = answers["versao_plataforma"];
            plataforma.app.description = answers["descricao"];
            plataforma.app.author = answers["autor"];
            fs.writeFileSync(path+"/plataforma.json",JSON.stringify(plataforma, null, 4),"UTF-8");
        });
    }

    getQuestions(){
        var questions = [];

        var q0 = {
            type: "input",
            default: "Domain.App",
            name: "nome",
            message: "Nome da Aplicação"
       };

        var q1 = {
             type: "input",
             name: "versao_plataforma",
             message: "Versão da Plataforma"
        };

        var q2 = {
            type: "input",
            name: "descricao",
            message: "Descrição"
        };

        var q3 = {
            type: "input",
            name: "autor",
            message: "Autor"
        };
         
        questions.push(q0,q1,q2,q3);
        return questions;
     }
}