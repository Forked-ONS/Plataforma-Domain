#!/usr/bin/env node
/**
 * A aplicacao principal carrega os módulos;
 * Lista todos os arquivos YAML que foram criados para o usuário
 * Monta o modelo de dominio em memoria
 * Converte o modelo para Sequelize
 * Gera o pacote de aplicacao através do Bundler
 *
 */
var FileLoader = require("./file_loader.js");
var ModelBuilder = require("./model_builder.js");
var Bundler = require("./bundler.js");

var runAppAction = new (require("./actions/runAppAction"));
var compileAppAction = new (require("./actions/compileAppAction"));
var createAppAction = new (require("./actions/createAppAction"));
var deployAppAction = new (require("./actions/deployAppAction"));
var cleanAppAction = new (require("./actions/cleanAppAction"));
var installPlatformAction = new (require("./actions/installPlatformAction"));
var stopPlatformAction = new (require("./actions/stopPlatformAction"));
var startPlatformAction = new (require("./actions/startPlatformAction"));
var upgradeComponentAction = new (require("./actions/upgradeComponentAction"));
var uninstallPlatformAction = new (require("./actions/uninstallPlatformAction"));
var remoteAction = new(require("./remote/actions/remote"))
var program = require('commander');
var fs = require("fs");
var os = require("os");
var shell = require("shelljs");
program
  .version('0.0.1')
  .option('-r, --run', 'Start app container')
  .option('-n, --new [type]', 'Creates a new App')
  .option('-t, --tecnology [tecnology]', 'Indica a tecnologia utilizada pelo App: node (default), dotnet.')
  .option('-d, --deploy [env]', 'Deploy App')
  .option('-c, --clean', 'Clean App')
  .option('-i, --install', 'Install Platform')
  .option('-s, --stop', 'Stop Platform')
  .option('-o, --compile', 'Compile App')
  .option('-st, --start', 'Sart Platform')
  .option('-mm, --metamapa', 'Mapas e Metadados')
  .option('-up, --upgrade', 'Faz o upgrade de algum componente da plataforma')
  .option('-un, --uninstall', 'Remove todos os componentes de plataforma')
  .option('-rt, --remote', 'Configura o cli para trabalhar em modo remoto')
  .option('-is, --install-solution [env]', 'Instala a solution no ambiente informado no comando')
  .option('-ia, --install-app [env]', 'Instala o app no ambiente informado no comando')
  .option('-ipk, --install-public-key [env]', 'Instala o app no ambiente informado no comando')
  .parse(process.argv);

if (program.new) createAppAction.exec(program.new, program.tecnology);
else if (program.install) installPlatformAction.exec();
else if (program.stop) stopPlatformAction.exec();
else if (program.start) startPlatformAction.exec();
else if (program.upgrade) upgradeComponentAction.exec(program.args);
else if (program.uninstall) uninstallPlatformAction.exec();
else if (program.remote) remoteAction.exec();
else if (!fs.existsSync("plataforma.json")) {
  console.log("Não é uma aplicação de plataforma válida");
  process.exit(-1);
}
if (program.compile) {
  compileAppAction.exec();
}
else if (program.run) {
  runAppAction.exec();
}
else if (program.clean) {
  cleanAppAction.exec(program.deploy);
}
else if (program.deploy) {
  deployAppAction.metamapa = program.metamapa;
  deployAppAction.exec(program.deploy);
}
else if(program.installSolution) {
  (new (require("./remote/actions/installSolution/installSolution"))()).exec();
}
else if(program.installPublicKey) {
  (new (require("./remote/actions/uploadPublicKey/uploadPublicKey"))()).exec();
}
else if(program.installApp) {
  (new (require("./remote/actions/installApp/installApp"))()).exec();
}




