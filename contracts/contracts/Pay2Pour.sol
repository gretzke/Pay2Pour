pragma solidity ^0.4.24;

contract Pay2Pour {
    // price and owner variables
    // owner set to private to demonstrate a view function
    uint256 public price;
    address private owner;

    // events to notify the frontend when price is changed or a new order comes in
    event newOrder(address indexed customerAccount, uint256 amount);
    event newPrice(uint256 oldPrice, uint256 newPrice);
    
    // function modifier that checks if caller of the function is the owner
    modifier onlyOwner() {
        require(msg.sender == owner);
        _;
    }
    
    // constructor of the smart contract, gets called on initialization
    constructor(uint256 _price) public {
        price = _price;
        owner = msg.sender;
    }
    
    // fallback function
    // accepts ether through "payable" keyword
    function () public payable {
        // ether sent to contract must be greater or equal to price
        require(msg.value >= price);
        // calculate number of drinks
        uint256 amount = msg.value / price;
        // refund remainder back to buyer
        msg.sender.transfer(msg.value % price);
        // emit newOrder event to notify device
        emit newOrder(msg.sender, amount);
    }
    
    // payout function only callable by owner
    function payout() public onlyOwner {
        // transfer the balance of the contract back to owner
        owner.transfer(address(this).balance);
    }
    
    // function to change the price only callable by owner
    function changePrice(uint256 _price) public onlyOwner {
        // price must be greater than 0
        require(_price > 0);
        // emit newPrice event to notify device
        emit newPrice(price, _price);
        // set variable
        price = _price;
    }
    
    // demonstration of a view function
    // returns address of owner
    function getOwner() public view returns (address) {
        return owner;
    }
}