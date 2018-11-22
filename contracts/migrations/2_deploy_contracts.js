var Pay2Pour = artifacts.require("./Pay2Pour.sol");

module.exports = function (deployer) {
    // deploy contract with a price of 0.015 ether
    deployer.deploy(Pay2Pour, web3.toWei(0.015, "ether"));
};