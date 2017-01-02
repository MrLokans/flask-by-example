(function(){
    'use strict';
    angular.module('WordcountApp', [])
        .controller('WordcountController', WordcountController);

    WordcountController.$inject = ['$scope', '$http', '$log'];

    function WordcountController($scope, $http, $log){
        $scope.getResults = function(){
            $log.log("Obtaining results for the job");

            var userInput = $scope.url;

            $http.post('/start', {'url': userInput}).
                success(function(results){
                    $log.log(results);
                }).
                error(function(error){
                    $log.error(error);
                });
        };
    }

}());