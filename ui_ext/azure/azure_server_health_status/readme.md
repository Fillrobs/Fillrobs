
Demonstrate Power-Status / VM-Status capabilities

Problem
	View to see Azure like console showing health status of all vms in real time
	have lots of accounts

Solution
Present a form with all Azure accounts within a drop-down


This plugin shows a table of Azure servers. With a Dropdown form to choose an RH of type Azure
with the output of the DescribeInstanceStatus which is part of the API (one call should get all instances from the associated account), 
loop includes per region...
So ServerName. power status and status rollup at per ec2 UI.

