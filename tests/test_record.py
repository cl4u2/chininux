from chininux import Record

r = Record("section", [
    "label1",
    "label2", 
    "label3", 
    "label4", 
    "label5",
    "label6",
    "label7",
    ])
r.label1 = "prova"
r.label2 = "10.0.1.0/24"
r.label3 = "10.0.2.0/30 (GR)"
r.label4 = "10.3.0.0/16 - 10.4.0.0/16"
r.label5 = "10.5.0.0/16 10.6.0.0/16"
r.label6 = "10.7.3.1 (GR)"
r.label7 = "10.7.3.2"

print "-" * 12

print r

print "-" * 12

assert r.search("10.0.1.1") > 0

assert r.search("10.0.2.1") > 0

assert r.search("10.3.3.1") > 0
assert r.search("10.4.3.1") > 0

assert r.search("10.5.3.1") > 0
assert r.search("10.6.3.1") > 0

assert r.search("10.7.3.1") > 0

assert r.search("10.7.3.2") > 0

assert r.search("10.8.3.2") == 0

print "test succeded"
