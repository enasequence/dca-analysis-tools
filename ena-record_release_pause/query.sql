-- this file must end in a new line
-- date format is dd-M-yyyy example: 02-JAN-2024
update study set hold_date = to_date('<the release date>') where trunc(hold_date) >= to_date('<starting the pause period date>') and trunc(hold_date) <= to_date('<end of the paused period date>');
update project set hold_date = to_date('<the release date>') where trunc(hold_date) >= to_date('<starting the pause period date>') and trunc(hold_date) <= to_date('<end of the paused period date>');
commit;

