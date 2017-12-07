/**
 * 
 * Este arquivo contem a estrutra do mapper em memoria
 * serve para reponder todas as perguntas referentes ao mapper
 */

'use strict';

class Index{

    constructor(maps){
        this.maps = maps;
        this.modelCache = {};
        this.projectionCache = {};
        this.functionsMap = {};
        this.includesMap = {};        
        if (Array.isArray(this.maps)){
            this.maps.forEach((r)=>this.parse(r));
            return;
        }
        throw typeof(this.maps) + " is not an Array";
    }

    //faz o parse do yaml do mapper para popular 
    //as estruturas de dados em memoria
    parse(register) {
        this.modelCache[register.appName] = register.map;
        this.generateIndex(register);
    }

    //Monta todo o index para facilitar a conversao entre modelos
    generateIndex(register){
        var processId = register.appName;
        var _map = register.map;        
        this.projectionCache[processId] = {};
        var projections = this.projectionCache[processId];
        for(var mappedModel in _map){
          var entity = _map[mappedModel].model;
          projections[mappedModel] = {};
          projections[mappedModel].attributes = [];
          for(var field in _map[mappedModel].fields){
            var fieldObj = _map[mappedModel]["fields"][field];
            if (fieldObj.type && fieldObj.type === "function"){
              this.functionsMap[processId] = {}
              this.functionsMap[processId][mappedModel] = {};
              this.functionsMap[processId][mappedModel][field] = fieldObj;
              continue;//ignora campos calculados
            }else if (fieldObj.type && fieldObj.type === "include"){
              this.includesMap[processId] = {}
              this.includesMap[processId][mappedModel] = {};
              this.includesMap[processId][mappedModel][field] = fieldObj;
              continue;//ignora campos de include
            }
            var proj = [fieldObj.column,field];
            projections[mappedModel].attributes.push(proj);        
          }
        }        
    }

    //retorna o mapa de uma aplicacao especifica
    getMapByAppId(appId)  {
        return this.modelCache[appId];
    }

    getMapByAppIdAndName(appId,name)  {
        return this.modelCache[appId][name];
    }

    getProjection(appId) {
        return this.projectionCache[appId];
    }

    getIncludes(processId,mapName) {
        return this.includesMap[processId][mapName];        
    };
    
    getFilters(processId,mapName) {
        return this.modelCache[processId][mapName]["filters"];        
    };

    getModelName(processId,mapName){    
        var _map = this.getMapByAppId(processId);
        return _map[mapName].model;
    }

    hasFunctions(processId, mapName){
        return this.functionsMap[processId] && this.functionsMap[processId][mapName];
    }

}

 module.exports = Index;