var shell = require("shelljs");
var os = require("os");
var fs = require("fs");
module.exports = class Ports{

    path(){
        return os.tmpdir();
    }
    /**
     * @description este método retorna uma próxima porta
     * disponível para ser usada por uma aplicação
     */
    getNextAvailablePort(){
        return 9110;
    }

    getUsedPorts(){
        return this.getInstalledApps().map(app => {
            try{
                var instance = JSON.parse(fs.readFileSync(this.path()+"/"+app+"/plataforma.instance.lock"));
                return instance.docker.port;
            }catch(e){
                return 9209;
            }

        }).sort();
    }

    getInstalledApps(){
        return shell.ls(this.path()).filter(item => {
            return item.indexOf("plataforma_") === 0;
        });
    }
};