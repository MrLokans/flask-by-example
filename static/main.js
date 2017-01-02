(function(){
    'use strict';
    angular.module('WordcountApp', [])
        .controller('WordcountController', WordcountController);

    WordcountController.$inject = ['$scope', '$http', '$timeout', '$log'];

    function WordcountController($scope, $http, $timeout, $log){
        $scope.getResults = function(){
            $log.log("Obtaining results for the job");

            var userInput = $scope.url;

            $http.post('/start', {'url': userInput}).
                success(function(results){
                    $log.log("Job " + results + " created.");
                    getWordCount(results);
                }).
                error(function(error){
                    $log.error(error);
                });
        };

        function getWordCount(jobID){
            var timeout = "";

            var poller = function(){
                $log.log("Polling data");
                $http.get('/results/' + jobID).
                    success(function(data, status, headers, config){
                        if (status === 202){
                            $log.log("Data is not ready yet.");
                            $log.log(data, status);
                        } else if (status === 200){
                            $log.info("Data obtained, stop polling.");
                            $log.log(data);
                            $scope.wordcounts = data;
                            $timeout.cancel(timeout);
                            return false;
                        } else {
                            $log.error("Unknown status code obtained: " + status);
                            $log.info(data);
                        }
                        // Poll results every two seconds
                        timeout = $timeout(poller, 2000);
                    })
                    .error(function(error){
                        $log.log("Error polling the data");
                        $log.log(error);
                    });
            };
            poller();
        }
    }


}());