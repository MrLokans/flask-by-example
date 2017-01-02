(function(){
    'use strict';
    angular.module('WordcountApp', [])
        .controller('WordcountController', WordcountController)
        .directive('wordCountChart', ['$parse', function($parse){

            function link(scope, element, attrs){
                scope.$watch('wordcounts', function(){
                    d3.select('#chart').selectAll('*').remove();
                    var data = scope.wordcounts;
                    for (var word in data){
                        d3.select('#chart')
                          .append('div')
                          .selectAll('div')
                          .data(word)
                          .enter()
                          .append('div')
                          .style('width', function(){
                            var width = data[word][1] * 40;
                             return width + 'px';
                          })
                          .text(function(d){
                            return data[word][0];
                          });
                    }
                }, true);
            }
            return {
                restrict: 'E',
                replace: true,
                template: '<div id="chart"></div>',
                link: link
            };
        }]);

    WordcountController.$inject = ['$scope', '$http', '$timeout', '$log'];

    function WordcountController($scope, $http, $timeout, $log){
        $scope.submitButtonText = 'Submit';
        $scope.loading = false;
        $scope.getResults = function(){
            $log.log("Obtaining results for the job");

            var userInput = $scope.url;

            $http.post('/start', {'url': userInput}).
                success(function(results){
                    $log.log("Job " + results + " created.");
                    getWordCount(results);
                    $scope.wordcounts = null;
                    $scope.loading = true;
                    $scope.submitButtonText = 'Loading...';
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
                            $scope.loading = false;
                            $scope.submitButtonText = "Submit";
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