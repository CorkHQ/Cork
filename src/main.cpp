#include <iostream>
#include "runners/wine.hpp"

int main(int, char**){
    cork::runners::WineRunner runner = cork::runners::WineRunner();

    runner.Execute({"winecfg"});
}
