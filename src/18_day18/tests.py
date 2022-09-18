import unittest
from pathlib import Path

import ansa
from ansa import base, constants

from card_handlers import card_handler, get_card_ent
from creators import (
    create_boundary_spc,
    create_box_v1,
    create_contact,
    create_initial_velocity,
    create_mat,
    create_plate_v1,
    create_sec,
    create_set,
)
from ctxmgr import MyImportV1
from id_grabbers import (
    get_fit_id_range,
    get_fit_mix_id_range,
    get_id,
    get_mat_prop_id,
    get_mix_id,
)
from schemas import ContactType, ControlCardType, LSDYNAType
from utils import output_file


class TestBoxDropBase(unittest.TestCase):
    deck = constants.LSDYNA

    def setUp(self):
        self._setup()

    def tearDown(self):
        self._tear_down()

    def _setup(self):
        pass

    def _tear_down(self):
        ents = base.CollectEntities(self.deck, None, LSDYNAType.ALL)
        base.DeleteEntity(ents)


class TestCreators(TestBoxDropBase):
    def test_create_mat(self):
        mat = create_mat()
        mat_id, mat_name = mat._id, mat._name
        self.assertEqual(mat_id, 1)
        self.assertIn('auto', mat_name)

    def test_create_mat_given_name(self):
        given_mat_name = 'dummy_mat_name'
        mat = create_mat(name=given_mat_name)
        mat_name = mat._name
        self.assertEqual(given_mat_name, mat_name)
        self.assertNotIn('auto', mat_name)

    def test_create_mat_given_vals(self):
        e = 123456
        vals = {'E': e}
        mat = create_mat(vals=vals)
        e_value = mat.get_entity_values(self.deck, ['E'])['E']
        self.assertEqual(e, e_value)

    def test_create_prop(self):
        prop = create_sec()
        prop_id, prop_name = prop._id, prop._name
        self.assertEqual(prop_id, 1)
        self.assertIn('auto', prop_name)

        mat = prop.get_entity_values(self.deck, ['MID'])['MID']
        mat_id, mat_name = mat._id, mat._name
        self.assertEqual(mat_id, 1)
        self.assertIn('auto', mat_name)

    def test_create_prop_given_name(self):
        given_prop_name = 'dummy_prop_name'
        prop = create_sec(name=given_prop_name)
        prop_name = prop._name
        self.assertEqual(given_prop_name, prop_name)
        self.assertNotIn('auto', prop_name)

    def test_create_prop_given_vals(self):
        t1 = 2
        vals = {'T1': t1}
        prop = create_sec(vals=vals)
        t1_value = prop.get_entity_values(self.deck, ['T1'])['T1']
        self.assertEqual(t1, t1_value)

    def test_create_set(self):
        set_ = create_set()
        set_id, set_name = set_._id, set_._name
        self.assertEqual(set_id, 1)
        self.assertIn('auto', set_name)

    def test_create_set_given_name(self):
        given_set_name = 'dummy_set_name'
        set_ = create_set(name=given_set_name)
        set_name = set_._name
        self.assertEqual(given_set_name, set_name)
        self.assertNotIn('auto', set_name)

    def test_create_set_add_prop(self):
        prop = create_sec()
        set_ = create_set(prop)

        prop_ents = base.CollectEntities(self.deck, set_, LSDYNAType.PROPERTY)
        self.assertEqual(len(prop_ents), 1)

        all_ents = base.CollectEntities(self.deck, set_, LSDYNAType.ALL)
        self.assertEqual(len(all_ents), 1)

    def test_create_contact(self):
        set1 = create_set()
        set2 = create_set()
        contact = create_contact(ssid=set1._id,
                                 msid=set2._id,
                                 sstyp=ContactType.TYPE2_PART_SET.value,
                                 mstyp=ContactType.TYPE2_PART_SET.value)
        contact_id, contact_name = contact._id, contact._name
        self.assertEqual(contact_id, 1)
        self.assertIn('auto', contact_name)


class TestID(TestBoxDropBase):
    def test_get_mat_prop_id(self):
        for _ in range(10):
            create_sec()
        create_mat()
        mat_prop_id = get_mat_prop_id()
        self.assertEqual(mat_prop_id, 12)

    def test_get_id(self):
        for _ in range(10):
            create_set()
        set_id = get_id(LSDYNAType.SET)
        self.assertEqual(set_id, 11)

    def test_mix_id(self):
        for _ in range(5):
            create_sec()
        for _ in range(10):
            create_set()
        mix_id = get_mix_id([LSDYNAType.PROPERTY, LSDYNAType.SET])
        self.assertEqual(mix_id, 11)

    def test_get_fit_id_range(self):
        create_mat()
        create_mat(vals={'MID': 10})
        start, end_ = get_fit_id_range(8, LSDYNAType.MATERIAL)
        self.assertEqual(start, 2)
        self.assertEqual(end_, 10)

    def test_get_fit_mix_id_range(self):
        create_mat()
        create_mat(vals={'MID': 10})
        create_sec()
        for _ in range(11):
            create_set()
        start, end_ = get_fit_mix_id_range(8, [LSDYNAType.MATERIAL,
                                               LSDYNAType.PROPERTY,
                                               LSDYNAType.SET])
        self.assertEqual(start, 12)
        self.assertEqual(end_, 20)


class TestMisc(TestBoxDropBase):
    def test_create_boundary_spc(self):
        c = 123456
        set_ = create_set()
        set_id = set_._id
        fields = ('NSID', 'c')
        boundary_spc = create_boundary_spc(dict(zip(fields, (set_id, c))))
        card_values = boundary_spc.get_entity_values(self.deck, fields)
        spc_nsid, spc_c = card_values['NSID']._id, card_values['c']
        self.assertEqual(spc_nsid, set_id)
        self.assertEqual(spc_c, c)

    def test_create_boundary_spc_c_str(self):
        c = '123456'
        set_ = create_set()
        set_id = set_._id
        fields = ('NSID', 'c')
        boundary_spc = create_boundary_spc(dict(zip(fields, (set_id, c))))
        card_values = boundary_spc.get_entity_values(self.deck, fields)
        spc_nsid, spc_c = card_values['NSID']._id, card_values['c']
        self.assertEqual(spc_nsid, set_id)
        self.assertNotEqual(spc_c, c)

    def test_create_initial_velocity(self):
        vz = -500
        box_set = create_set()
        box_set_id = box_set._id
        fields = ('NSID', 'VZ')
        initial_velocity = create_initial_velocity(
            dict(zip(fields, (box_set_id, vz))))
        card_values = initial_velocity.get_entity_values(self.deck, fields)
        iv_nsid, iv_vz = card_values['NSID']._id, card_values['VZ']
        self.assertEqual(iv_nsid, box_set_id)
        self.assertEqual(iv_vz, vz)

    def test_create_ctrl_card(self):
        endtim = 1.5E-2
        crtl_ent = get_card_ent(ControlCardType.CONTROL)
        ctrl_params = [('TERMINATION', {'ENDTIM': endtim})]
        crtl_ent = card_handler(crtl_ent, ctrl_params)
        fields = ('TERMINATION', 'TERMINATION_ENDTIM')
        card_values = crtl_ent.get_entity_values(self.deck, fields)
        termination, termination_endtim = card_values.values()
        self.assertEqual(termination, 'ON')
        self.assertEqual(termination_endtim, endtim)

    def test_create_db_card(self):
        dt = 2E-4
        db_ent = get_card_ent(ControlCardType.DATABASE)
        db_params = [('D3PLOT', {'DT': dt})]
        db_ent = card_handler(db_ent, db_params)
        fields = ('D3PLOT', 'D3PLOT_DT')
        card_values = db_ent.get_entity_values(self.deck, fields)
        db, db_d3plot = card_values.values()
        self.assertEqual(db, 'ON')
        self.assertEqual(db_d3plot, dt)

    def test_output_file(self):
        filename = 'lsdyna_test_file.k'
        p = Path(output_file(filename, self.deck))
        self.assertTrue(p.is_file())
        with open(p) as f:
            try:
                self.assertIn('ANSA', f.read(30))
            except AssertionError as ex:
                raise ex
            finally:
                p.unlink()


class TestPlate(TestBoxDropBase):
    def _setup(self):
        self.l, self.w, self.en1, self.en2 = 100, 100, 10, 10
        self.z_elv, self.move_xy, self.rot_angle = 0, None, None

    def test_create_plate_v1(self):
        plate_prop = create_sec()
        plate_mat_prop_id = plate_prop._id
        plate_set = create_set(plate_prop, 'plate', deck=self.deck)
        plate_import_v1 = MyImportV1()
        with plate_import_v1 as import_v1:
            create_plate_v1(import_v1,
                            self.l,
                            self.w,
                            self.en1,
                            self.en2,
                            plate_mat_prop_id,
                            z_elv=self.z_elv,
                            move_xy=self.move_xy,
                            rot_angle=self.rot_angle,
                            deck=self.deck)

        n_nodes = (self.en1+1)*(self.en2+1)
        n_shells = self.en1*self.en2
        self.assertEqual(len(plate_import_v1.nodes), n_nodes)
        self.assertEqual(len(plate_import_v1.shells), n_shells)


class TestBox(TestBoxDropBase):
    def _setup(self):
        self.l, self.w, self.h, self.en1, self.en2, self.en3 = 50, 50, 50, 10, 10, 10
        self.z_elv, self.move_xy, self.rot_angle = 5, (50, 20), 45

    def test_create_box_v1(self):
        box_prop = create_sec()
        box_mat_prop_id = box_prop._id
        box_set = create_set(box_prop, 'box', deck=self.deck)
        box_import_v1 = MyImportV1()
        with box_import_v1 as import_v1:
            create_box_v1(import_v1,
                          self.l,
                          self.w,
                          self.h,
                          self.en1,
                          self.en2,
                          self.en3,
                          box_mat_prop_id,
                          z_elv=self.z_elv,
                          move_xy=self.move_xy,
                          rot_angle=self.rot_angle,
                          deck=self.deck)

        n_nodes = (self.en1+1)*(self.en2+1)*(self.en3+1)
        n_solids = self.en1*self.en2*self.en3
        self.assertEqual(len(box_import_v1.nodes), n_nodes)
        self.assertEqual(len(box_import_v1.solids), n_solids)


if __name__ == '__main__':
    unittest.main()
